"""s6469 G1c: ground-presence score + side-by-side sheet across dd arms.
Usage: g1c_ground_sheet.py out.png label=run_dir ...   (flight fbs 0x80620000/0x80690000, stride 512)
Score = fraction of pixels in the bottom band (rows 60-90% of height, x 60..w-60) that are NOT sky-blue
(sky-blue = b > r+8 and b > g+8, same test terr() inverts in g1c_fbdump_join.py). Ground present -> high; missing -> ~0."""
import sys, os, re, statistics as st
from PIL import Image
FB = {0x80620000, 0x80690000}
def window(d):
    o = []
    for ln in open(os.path.join(d, "run.log"), errors="replace"):
        m = re.match(r"\[fbdump\] n=(\d+) fb=(0x[0-9A-Fa-f]+) stride=512", ln)
        if m and int(m.group(2), 16) in FB: o.append(int(m.group(1)))
    return o
def load(d, n):
    p = os.path.join(d, "fbd", "fb_%07d_w512.ppm" % n)
    return Image.open(p).convert("RGB") if os.path.exists(p) else None
def ground(im):
    w, h = im.size; px = im.load(); t = n = 0
    for y in range(int(h*.6), int(h*.9)):
        for x in range(60, w-60, 2):
            r, g, b = px[x, y]; n += 1
            if not (b > r+8 and b > g+8): t += 1
    return t/n
arms = [a.split("=", 1) for a in sys.argv[2:]]
tiles = []
for lab, d in arms:
    ns = window(d); ns = ns[len(ns)//10:]
    sc = []; keep = None
    for i, n in enumerate(ns[::max(1, len(ns)//12)]):
        im = load(d, n)
        if im is None: continue
        sc.append(ground(im))
        if keep is None and i == 6: keep = im
    if keep is None and sc: keep = im
    print("%-8s frames=%d ground med %.3f min %.3f max %.3f" % (lab, len(sc), st.median(sc), min(sc), max(sc)))
    tiles.append(keep)
w, h = tiles[0].size
sheet = Image.new("RGB", (w*2, h*((len(tiles)+1)//2)))
for i, t in enumerate(tiles): sheet.paste(t, ((i % 2)*w, (i//2)*h))
sheet.save(sys.argv[1])
