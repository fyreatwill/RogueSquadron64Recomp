#!/usr/bin/env python3
"""s7165: find letterboxed cutscene swaps in an angrylion replay dir (f<swap>.rgb) and report per-swap unpainted px from <dir>.log.
usage: s7165_letterbox.py <replaydir>   (letterbox = top 8% and bottom 8% rows near-black while the middle is not)
Positive control: scratch/s7141/L4wr (s7165, 21:9 dd4) must list 7890-7995 with the 7928-7955 unpainted burst."""
import importlib.util, os, sys
from PIL import ImageStat
spec = importlib.util.spec_from_file_location('F', os.path.join(os.path.dirname(__file__), 's7122_fidelity.py'))
F = importlib.util.module_from_spec(spec); spec.loader.exec_module(F)
d = sys.argv[1].rstrip('/'); up = {}
for l in open(d + '.log'):
    t = l.split(); up[int(t[1])] = int(t[11]) - int(t[9])
lb = []
for s in sorted(up):
    p = os.path.join(d, 'f%d.rgb' % s)
    if not os.path.exists(p): continue
    im = F.load_al(p).convert('L'); w, h = im.size; k = int(h * 0.08)
    top = ImageStat.Stat(im.crop((0, 0, w, k))).mean[0]; bot = ImageStat.Stat(im.crop((0, h - k, w, h))).mean[0]
    mid = ImageStat.Stat(im.crop((0, h // 3, w, 2 * h // 3))).mean[0]
    if top < 6 and bot < 6 and mid > 20: lb.append(s)
runs = []
for s in lb:
    if runs and s - runs[-1][1] <= 3: runs[-1][1] = s
    else: runs.append([s, s])
print('swaps', len(up), 'letterboxed', len(lb), 'runs', runs)
for a, b in runs:
    u = [up[s] for s in range(a, b + 1) if s in up]
    print('  %d-%d n %d unpainted max %d swaps>200 %d' % (a, b, len(u), max(u), sum(x > 200 for x in u)))
print('all-swap unpainted>200:', sum(v > 200 for v in up.values()))
