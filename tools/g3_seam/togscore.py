# s6794: score toggled window shots per arm. Arm from shot file mtime (epoch): mode seam = (t/2)%3 (ROGUESQ_SEAM_TOG, 2 s
# arms, 0.3 s boundary margin); mode exact = int(t)&1 (ROGUESQ_EXACT_EDGES=tog, 1 s arms, 0.15 s margin). Per shot: best dark-column fraction (seamscan.py metric) and column.
# Args: shot dir [seam|exact].
import os, sys, collections
from PIL import Image
d = sys.argv[1]; mode = sys.argv[2] if len(sys.argv) > 2 else 'seam'; per = collections.defaultdict(list)
for f in sorted(f for f in os.listdir(d) if f.endswith('.png')):
    p = os.path.join(d, f); t = os.path.getmtime(p)
    per_s, m = (2.0, 0.3) if mode == 'seam' else (1.0, 0.15)
    ph = t % per_s
    if ph < m or ph > per_s - m: continue
    arm = int(t // 2) % 3 if mode == 'seam' else int(t) & 1
    im = Image.open(p).convert('L')
    if im.size != (1280, 1024): continue
    px = im.load(); ys = range(300, 800, 2)
    if sum(px[640, y] for y in ys) / len(ys) < 8: continue
    best = (0, 0)
    for x in range(600, 681):
        c = sum(1 for y in ys if px[x, y] + 12 <= px[x - 4, y] and px[x, y] + 12 <= px[x + 4, y]) / len(ys)
        best = max(best, (c, x))
    per[arm].append((f[2:9], best[1], round(best[0], 2)))
for arm in sorted(per):
    L = per[arm]; hit = [h for h in L if h[2] >= 0.3]
    print('arm', arm, 'lit', len(L), 'line', len(hit), ' '.join('%s:%d:%.2f' % h for h in L))
