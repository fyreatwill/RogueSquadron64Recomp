#!/usr/bin/env python3
"""s7148: per-swap presented-frame search. The s7122 scorer joins swap->presented frame with ONE global lag; on fast cutscene motion
at FPS60 (render-only frames between swaps) that join can pick a neighbour frame and score motion as a render diff. For each swap,
search pframe in [p-K, p+K] for min mean|d| and report frac>T at the nominal and the best frame, plus the offset chosen.
usage: s7148_pfsearch.py raw aldir frames.csv rect(x0,y0,x1,y1) [K=20] [out.csv]"""
import sys, os, csv, statistics as S, importlib.util
sp = importlib.util.spec_from_file_location('f', os.path.join(os.path.dirname(os.path.abspath(__file__)), 's7122_fidelity.py')); F = importlib.util.module_from_spec(sp); sp.loader.exec_module(F)
from PIL import Image
raw = F.Raw(sys.argv[1]); ald = sys.argv[2]; R = tuple(map(int, sys.argv[4].split(','))); W, H = R[2] - R[0], R[3] - R[1]
K = int(sys.argv[5]) if len(sys.argv) > 5 else 20; out = sys.argv[6] if len(sys.argv) > 6 else None
def sc(a, p): d = F.dmap(a, p); return sum(d) / len(d), sum(v > F.T for v in d) / len(d)
res = []
for r in csv.DictReader(open(sys.argv[3])):
    p0 = int(r['pframe']); al = F.load_al(os.path.join(ald, 'f%s.rgb' % r['swap']))
    if al is None: continue
    al = al.resize((W, H), Image.BOX)
    c = {q: sc(al, raw.img(q).crop(R)) for q in range(max(0, p0 - K), min(len(raw.T), p0 + K + 1))}
    b = min(c, key=lambda q: c[q][0]); res.append((r['swap'], p0, b - p0, c[p0][1], c[b][0], c[b][1]))
    print('%s p%d off%+d frac nominal %.4f best md %.2f frac %.4f' % res[-1], flush=True)
print('N', len(res), 'median frac nominal %.4f best %.4f' % (S.median(x[3] for x in res), S.median(x[5] for x in res)), 'offsets', sorted(set(x[2] for x in res)))
if out:
    w = csv.writer(open(out, 'w')); w.writerow(['swap', 'pframe', 'off', 'frac_nom', 'md_best', 'frac_best']); w.writerows(res)
