#!/usr/bin/env python3
"""s7165: letterboxed-cutscene spans in a g5b_capture presented raw (whole capture, every <step>-th frame).
usage: s7165_rawlb.py <raw> [rect=1,11,469,216] [step=4]. Prints spans as presented-frame index and seconds from capture start.
Positive control: scratch/s7141/L4w.raw must show the span that the replay (s7165_letterbox.py) found at swaps 7885-8083."""
import importlib.util, os, sys
from PIL import ImageStat
spec = importlib.util.spec_from_file_location('F', os.path.join(os.path.dirname(__file__), 's7122_fidelity.py'))
F = importlib.util.module_from_spec(spec); spec.loader.exec_module(F)
raw = F.Raw(sys.argv[1]); R = tuple(map(int, (sys.argv[2] if len(sys.argv) > 2 else '1,11,469,216').split(',')))
st = int(sys.argv[3]) if len(sys.argv) > 3 else 4; H = R[3] - R[1]; k = int(H * 0.08); t0 = raw.T[0]; spans = []
for i in range(0, len(raw.T), st):
    im = raw.img(i).crop(R).convert('L'); w = im.size[0]
    top = ImageStat.Stat(im.crop((60, 0, w - 60, k))).mean[0]; bot = ImageStat.Stat(im.crop((60, H - k, w - 60, H))).mean[0]
    mid = ImageStat.Stat(im.crop((0, H // 3, w, 2 * H // 3))).mean[0]
    if top < 8 and bot < 8 and mid > 20:
        if spans and i - spans[-1][1] <= 3 * st: spans[-1][1] = i
        else: spans.append([i, i])
print(sys.argv[1], 'frames', len(raw.T), 'dur %.1fs' % ((raw.T[-1] - t0) / 1e9))
for a, b in spans: print('  frames %d-%d  t %.1f-%.1f s' % (a, b, (raw.T[a] - t0) / 1e9, (raw.T[b] - t0) / 1e9))
