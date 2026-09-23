"""Generate a Markdown table and standalone SVG from measured JSON (stdlib only)."""
from collections import defaultdict
import html
import json
from pathlib import Path
import statistics
import sys

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "benchmarks/20260923_results.json").read_text())
groups = defaultdict(list)
for run in data["runs"]:
    groups[(run["version"], run["jit_enabled"])].append(run)
assert len(data["runs"]) == 24 and len(groups) == 8
assert all(len(runs) == 3 for runs in groups.values())
rows = []
for (version, enabled), runs in groups.items():
    runs.sort(key=lambda run: run["repetition"])
    values = [run["seconds"] for run in runs]
    mode = "ON" if enabled else ("OFF" if runs[0]["jit_available"] else "N/A")
    rows.append((version, mode, values, statistics.mean(values)))
rows.sort(key=lambda row: (tuple(int(x) for x in row[0].split(".")[:2]), row[1] == "ON"))

lines = [
    "# Python rendering benchmark — 2026-09-23", "",
    "Windows 11 x64; Intel Core i7-12700K; official CPython Windows embeddable builds.", "",
    "Input: `flourish.mid` + `TimGM6mb.sf2`; 44,100 Hz stereo; 3,858,749 frames (about 87.5 seconds).",
    "Only `sequencer.render(left, right)` is timed using `time.perf_counter()`. Input loading, buffer allocation, output hashing and WAV saving are excluded.",
    "Each measurement uses a fresh process with no warmup. JIT compilation during render is included. Runs are sequential; case order is reversed in round 2. Values below are seconds; averages use unrounded measurements.", "",
    "| Python | JIT | Run 1 | Run 2 | Run 3 | Mean |",
    "|---|---|---:|---:|---:|---:|",
]
for version, mode, values, mean in rows:
    lines.append(f"| {version} | {mode} | " + " | ".join(f"{v:.3f}" for v in values) + f" | **{mean:.3f}** |")
lines += ["", "![Rendering time](../media/20260923_python_rendering_time.svg)", "",
    "Bars show arithmetic means; thin whiskers show minimum–maximum across three runs. Lower is faster. N/A means JIT is unavailable in the tested build; it does not mean a zero runtime.", "",
    "Python 3.10's second run was noticeably slower than its other two runs. It is retained in the mean; the cause was not established.", "",
    "Python 3.10.11, 3.11.9 and 3.12.10 are the last official Windows binary releases in those series, not their latest source-only security releases. Python 3.13.15 and 3.14.7 are the latest stable releases as of the measurement date. Python 3.15.0rc2 is a prerelease. The 3.13 official build used here has no JIT support; no custom Python builds were made.", "",
    "Sources: [Python releases](https://www.python.org/downloads/), [3.10 binary availability](https://www.python.org/downloads/release/python-31021/), [3.11 binary availability](https://www.python.org/downloads/release/python-31116/), [3.12 binary availability](https://www.python.org/downloads/release/python-31214/), [3.15.0rc2](https://www.python.org/downloads/release/python-3150rc2/).", "",
    f"Distinct rendered-output SHA-256 hashes across all 24 measurements: {len(set(run['output_sha256'] for run in data['runs']))}.",
    "Raw measurements, build strings and input/code hashes: [20260923_results.json](20260923_results.json).", "",
    "The earlier one-off 3.14.7 measurement is excluded. Historical measurements for other languages in the old README graph were not rerun and are not combined with this benchmark.", "",
]
(ROOT / "benchmarks/20260923_results.md").write_text("\n".join(lines), encoding="utf-8")

# A dependency-free vector chart, also suitable for rasterization with bundled Sharp.
w, h = 1080, 760
left, top, scale = 235, 174, 9.0
max_seconds = max(max(row[2]) for row in rows)
axis_max = (int(max_seconds / 10) + 1) * 10
scale = 730 / axis_max
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
       '<rect width="1080" height="760" fill="#ffffff"/>',
       '<g font-family="Segoe UI, Arial, sans-serif" fill="#172b3a">',
       '<text x="42" y="48" font-size="29" font-weight="700">Py-MeltySynth · Python rendering benchmark</text>',
       '<text x="42" y="80" font-size="17" fill="#536778">flourish.mid + TimGM6mb.sf2 · 44.1 kHz stereo · 3 fresh-process runs per case</text>',
       '<text x="42" y="107" font-size="16" fill="#536778">Intel Core i7-12700K · Windows 11 x64 · 2026-09-23</text>',
       '<rect x="42" y="130" width="17" height="17" rx="3" fill="#206986"/>',
       '<text x="68" y="144" font-size="15">Standard / JIT OFF</text>',
       '<rect x="260" y="130" width="17" height="17" rx="3" fill="#df8638"/>',
       '<text x="286" y="144" font-size="15">JIT ON</text>',
       '<text x="520" y="144" font-size="15" fill="#536778">Whiskers: min–max · Lower is faster</text>']
bottom = top + len(rows) * 55
for tick in range(0, axis_max + 1, 10):
    x = left + tick * scale
    svg += [f'<line x1="{x}" y1="{top-10}" x2="{x}" y2="{bottom}" stroke="#dce5eb"/>',
            f'<text x="{x}" y="{bottom+27}" font-size="15" text-anchor="middle">{tick}</text>']
for i, (version, mode, values, mean) in enumerate(rows):
    y = top + i * 55
    color = "#df8638" if mode == "ON" else "#206986"
    label = version + (" · JIT " + mode if mode != "N/A" else "")
    svg += [f'<text x="{left-18}" y="{y+23}" text-anchor="end" font-size="18">{html.escape(label)}</text>',
            f'<rect x="{left}" y="{y}" width="{mean*scale:.3f}" height="34" rx="3" fill="{color}"/>']
    lo, hi = left + min(values)*scale, left + max(values)*scale
    svg += [f'<path d="M {lo:.3f} {y+17} H {hi:.3f} M {lo:.3f} {y+9} V {y+25} M {hi:.3f} {y+9} V {y+25}" fill="none" stroke="#172b3a" stroke-width="1.5"/>',
            f'<text x="{max(left+mean*scale,hi)+10:.3f}" y="{y+23}" font-size="17" font-weight="600">{mean:.2f}</text>']
svg += [f'<text x="{left+365}" y="{bottom+57}" text-anchor="middle" font-size="17">Rendering time (seconds)</text>',
        '<text x="42" y="710" font-size="14" fill="#536778">3.10–3.12: last official Windows binary releases. 3.15.0rc2: prerelease.</text>',
        '<text x="42" y="735" font-size="14" fill="#536778">Render only; setup / file I/O excluded. JIT compilation during render included. No warmup.</text>',
        '</g></svg>']
(ROOT / "media/20260923_python_rendering_time.svg").write_text("\n".join(svg), encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")
print("\n".join(lines[:18]))
