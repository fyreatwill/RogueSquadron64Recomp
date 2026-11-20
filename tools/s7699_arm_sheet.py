#!/usr/bin/env python3
"""s7699 owner sheet for the POOLMIN toggle run (tools/s7698_poolmin_rehold.zsh): consecutive intro fb dumps that sit in opposite
mach-second arms (even = s6908 floor 4096, odd = old per-level cap), the K pairs with the largest sky-fraction gap, floor left / old right.
Arm from dump mtime via the live wall-mach offset (host must not have slept since the run). Usage: s7699_arm_sheet.py <run dir> <level> <out.png> [K]"""
import sys, os, re, ctypes, time, statistics as st
from PIL import Image, ImageDraw
D, LV, OUT = sys.argv[1], int(sys.argv[2]), sys.argv[3]; K = int(sys.argv[4]) if len(sys.argv) > 4 else 4
lib = ctypes.CDLL(None); lib.mach_absolute_time.restype = ctypes.c_uint64
OFF = time.time() - lib.mach_absolute_time() / 24e6
L = open(D + "/run.log", errors="replace").read().splitlines()
cine = next(i for i, l in enumerate(L) if "[cineBody] call#" in l and re.search(r"a0=0x0*%X " % LV, l))
mis = next((i for i, l in enumerate(L) if i > cine and "[poolx] cap 2048" in l), len(L))
def img(p):
    b = open(p, "rb").read(); hd = []; o = 0
    while len(hd) < 4:
        e = b.index(b"\n", o); ln = b[o:e]; o = e + 1
        if not ln.startswith(b"#"): hd += ln.split()
    return Image.frombytes("RGB", (int(hd[1]), int(hd[2])), b[o:o + int(hd[1]) * int(hd[2]) * 3])
def sky(im):
    g = im.convert("L"); w, h = g.size; px = g.load(); s = st.median(px[x, 0] for x in range(w))
    v = [px[x, y] for y in range(int(h * 0.55), h, 3) for x in range(0, w, 3)]; return sum(abs(q - s) <= 12 for q in v) / len(v)
rows = []
for i in range(cine, mis):
    m = re.match(r"\[fbdump\] n=(\d+) .*stride=(\d+)", L[i])
    if not m: continue
    f = "%s/fb/fb_%07d_w%s.ppm" % (D, int(m[1]), m[2])
    if os.path.exists(f):
        t = os.stat(f).st_mtime - OFF
        if abs(t - round(t)) > 0.12: rows.append((int(m[1]), int(t) & 1, f))
pairs = []
for a, b in zip(rows, rows[1:]):
    if a[1] != b[1] and b[0] - a[0] <= 30:
        fl, old = (a, b) if a[1] == 0 else (b, a); ia, ib = img(fl[2]), img(old[2]); pairs.append((sky(ib) - sky(ia), fl, old, ia, ib))
pairs.sort(key=lambda p: -p[0]); sel = sorted(pairs[:K], key=lambda p: p[1][0])
W, H = sel[0][3].size; sh = Image.new("RGB", (2 * W + 6, K * (H + 14)), (40, 40, 40)); d = ImageDraw.Draw(sh)
for k, (g, fl, old, ia, ib) in enumerate(sel):
    y = k * (H + 14); sh.paste(ia.resize((W, H)), (0, y + 14)); sh.paste(ib.resize((W, H)), (W + 6, y + 14))
    d.text((2, y), "floor 4096 swap %d" % fl[0], fill="white"); d.text((W + 8, y), "old cap swap %d  sky +%.2f" % (old[0], g), fill="white")
sh.save(OUT); print("pairs=%d shown=%d gaps=%s -> %s" % (len(pairs), K, " ".join("%.2f" % p[0] for p in sel), OUT))
print("all-pair sky gap old-floor: mean=%.3f median=%.3f pos=%d/%d" % (st.mean(p[0] for p in pairs), st.median(p[0] for p in pairs), sum(p[0] > 0 for p in pairs), len(pairs)))
