# s6793: per window shot (1280x1024), find a 1-2 px dark vertical line near the screen centre: per column x in 600..680,
# fraction of cinematic rows (300..800) where the pixel is >=12 darker than both x-4 and x+4. Reports frames whose best
# column fraction >= 0.3 and the column histogram. Args: dirs.
import os, sys, collections
from PIL import Image
for d in sys.argv[1:]:
    fs = sorted(f for f in os.listdir(d) if f.endswith('.png')); hits = []; colh = collections.Counter(); n = 0
    for f in fs:
        im = Image.open(os.path.join(d, f)).convert('L')
        if im.size != (1280, 1024): continue
        px = im.load(); ys = range(300, 800, 2)
        if sum(px[640, y] for y in ys) / len(ys) < 8: continue
        n += 1; best = (0, 0)
        for x in range(600, 681):
            c = sum(1 for y in ys if px[x, y] + 12 <= px[x - 4, y] and px[x, y] + 12 <= px[x + 4, y]) / len(ys)
            best = max(best, (c, x))
        if best[0] >= 0.3: hits.append((f, best[1], round(best[0], 2))); colh[best[1]] += 1
    print(d, 'lit frames', n, 'line frames', len(hits), 'cols', colh.most_common(5)); print("  ", " ".join("%s:%d:%.2f" % (h[0][2:9], h[1], h[2]) for h in hits))
