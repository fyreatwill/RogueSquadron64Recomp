#!/usr/bin/env python3
"""s6902 G5c: how long the IMAGE stays frozen in a tools/g5b_capture .raw, not how long frames stop arriving. Presents can keep flowing while the picture
is unchanged, so g5b_drops' gap figures cannot see a freeze. A frozen run = consecutive byte-identical frames; its length runs from the first copy to the
next frame that differs. Prints runs >= min_ms by offset from the first frame.  Usage: g5c_frozen_runs.py x.raw [min_ms=150]"""
import struct, sys
path = sys.argv[1]; min_ms = float(sys.argv[2]) if len(sys.argv) > 2 else 150
f = open(path, 'rb'); t0, w, h = struct.unpack('<QII', f.read(16)); fs = w * h * 3; f.seek(0)
prev = None; T = []; same = []
while True:
    hd = f.read(16); b = f.read(fs)
    if len(hd) < 16 or len(b) < fs: break
    T.append((struct.unpack('<Q', hd[:8])[0] - t0) / 24e6); same.append(b == prev); prev = b
runs = []; i = 1
while i < len(T):
    if same[i]:
        j = i
        while j + 1 < len(T) and same[j + 1]: j += 1
        end = T[j + 1] if j + 1 < len(T) else T[j]
        runs.append(((end - T[i - 1]) * 1e3, T[i - 1], j - i + 1)); i = j + 1
    else: i += 1
print(f"frames {len(T)} span {T[-1]:.1f}s {w}x{h} identical-to-previous {sum(same)} runs {len(runs)} longest {max([r[0] for r in runs] or [0]):.0f} ms")
big = sorted([r for r in runs if r[0] >= min_ms], key=lambda r: r[1])
print(f"frozen runs >= {min_ms:.0f} ms: {len(big)}")
for ms, t, n in big[:30]: print(f"  at +{t:.2f}s frozen {ms:.0f} ms over {n} repeated frames")
