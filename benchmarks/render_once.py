"""One fresh-process render; uses only the Python standard library."""
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import meltysynth as ms

jit = getattr(sys, "_jit", None)
jit_available = jit.is_available() if jit else False
jit_enabled = jit.is_enabled() if jit else False
requested_jit = os.environ.get("PYTHON_JIT") == "1"
if requested_jit != jit_enabled:
    raise RuntimeError("Requested JIT state is not active")

sf = ms.SoundFont.from_file(str(ROOT / "TimGM6mb.sf2"))
settings = ms.SynthesizerSettings(44100)
synth = ms.Synthesizer(sf, settings)
midi = ms.MidiFile.from_file(str(ROOT / "flourish.mid"))
seq = ms.MidiFileSequencer(synth)
seq.play(midi, False)
left = ms.create_buffer(int(settings.sample_rate * midi.length))
right = ms.create_buffer(int(settings.sample_rate * midi.length))
start = time.perf_counter()
seq.render(left, right)
elapsed = time.perf_counter() - start

# Hashing is outside the timed region; retain evidence of identical output.
output_hash = hashlib.sha256(left.tobytes() + right.tobytes()).hexdigest()
print(json.dumps({
    "version": platform.python_version(), "build": sys.version,
    "executable": sys.executable, "platform": platform.platform(),
    "jit_available": jit_available, "jit_enabled": jit_enabled,
    "seconds": elapsed, "sample_rate": settings.sample_rate,
    "midi_seconds": midi.length, "frames": len(left),
    "output_sha256": output_hash,
}), flush=True)
