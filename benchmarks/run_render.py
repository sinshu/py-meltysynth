"""Run the six official Windows builds sequentially, three fresh processes each."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "benchmarks" / "20260923_results.json"
runtime_root = Path(sys.argv[1])
versions = ["3.10.11", "3.11.9", "3.12.10", "3.13.15", "3.14.7", "3.15.0rc2"]
cases = [(v, mode) for v in versions for mode in ([False, True] if v in versions[-2:] else [False])]
result = {
    "started_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "cpu": "12th Gen Intel Core i7-12700K",
    "method": "Sequential fresh processes; one render per process; no warmup; perf_counter around sequencer.render only; 3 rounds, reversed order in round 2; JIT compilation during render included; default GC; 44100 Hz stereo; no WAV writing.",
    "sources": {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                for name in ["meltysynth.py", "flourish.mid", "TimGM6mb.sf2"]},
    "runs": [],
}
for repetition in range(1, 4):
    order = cases if repetition != 2 else list(reversed(cases))
    for version, enabled in order:
        print(f"START round={repetition} Python={version} JIT={'ON' if enabled else 'OFF'}", flush=True)
        env = os.environ.copy()
        env["PYTHON_JIT"] = "1" if enabled else "0"
        completed = subprocess.run(
            [str(runtime_root / version / "python.exe"), "-B", str(ROOT / "benchmarks" / "render_once.py")],
            env=env, cwd=ROOT, text=True, capture_output=True, check=True,
        )
        run = json.loads(completed.stdout)
        if run["version"] != version:
            raise RuntimeError(f"Version mismatch: {run['version']} != {version}")
        run["repetition"] = repetition
        result["runs"].append(run)
        OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(f"DONE {run['seconds']:.6f} s ({len(result['runs'])}/24)", flush=True)
