"""s6486 G1c: fraction of magenta (FORCE_FOG=FF00FF) pixels per flight fbdump, whole frame and bottom band.
Usage: g1c_magenta.py run_dir [run_dir...]  (flight fbs 0x80620000/0x80690000)"""
import sys, os, re, statistics as st
from PIL import Image
FB = {0x80620000, 0x80690000}
for d in sys.argv[1:]:
    ns = []
    for ln in open(os.path.join(d, "run.log"), errors="replace"):
        m = re.match(r"\[fbdump\] n=(\d+) fb=(0x[0-9A-Fa-f]+) stride=512", ln)
        if m and int(m.group(2), 16) in FB: ns.append(int(m.group(1)))
    ns = ns[len(ns)//10:]; wh = []; bb = []
    for n in ns[::max(1, len(ns)//15)]:
        p = os.path.join(d, "fbd", "fb_%07d_w512.ppm" % n)
        if not os.path.exists(p): continue
        im = Image.open(p).convert("RGB"); w, h = im.size; px = im.load(); a = c = bt = bc = 0
        for y in range(0, h, 2):
            for x in range(0, w, 2):
                r, g, b = px[x, y]; mg = r > 150 and b > 150 and g < r - 60 and g < b - 60
                a += 1; c += mg
                if .6*h <= y < .9*h: bt += 1; bc += mg
        wh.append(c/a); bb.append(bc/bt)
    print(d, "frames", len(wh), "magenta whole med %.4f max %.4f | bottom-band med %.4f max %.4f" % (st.median(wh), max(wh), st.median(bb), max(bb)) if wh else "none")
