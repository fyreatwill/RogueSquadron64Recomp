#!/usr/bin/env python3
"""s7698: score a tools/s7698_poolmin_rehold.zsh run. [fbdump] lines are ordered against the level's [cineBody] intro call and the
mission [poolx] cap line, so dumps between them are the intro. ROGUESQ_DD_POOLMIN_TOG flips on mach seconds whose phase vs the dump
file mtimes is unknown, so the phase is fitted on the intro (max |arm difference| of lower-frame detail) and the SAME phase is then
applied to the flight dumps, where the toggle cannot act (mission cap 8192 = old): a real effect shows in the intro and not in flight.
Metric per dump: luminance stddev of the bottom 45% (ground detail) and the fraction of its pixels within 12 of the frame's top-row
median (sky-like). Usage: s7698_poolmin_phase.py <run dir> <level>"""
import sys, os, re, statistics as st
D, LV = sys.argv[1], int(sys.argv[2])
L = open(os.path.join(D, "run.log"), errors="replace").read().splitlines()
cine = next(i for i, l in enumerate(L) if "[cineBody] call#" in l and re.search(r"a0=0x0*%X " % LV, l))
mis = next(i for i, l in enumerate(L) if i > cine and "[poolx] cap 2048" in l)
def ppm(p):
    b = open(p, "rb").read(); hd = []; o = 0
    while len(hd) < 4:
        e = b.index(b"\n", o); ln = b[o:e]; o = e + 1
        if not ln.startswith(b"#"): hd += ln.split()
    return int(hd[1]), int(hd[2]), b[o:]
def score(p):
    w, h, px = ppm(p); y0 = int(h * 0.55); lum = []
    for y in range(y0, h, 3):
        r = px[(y * w) * 3:(y * w + w) * 3]
        lum += [(r[i] * 3 + r[i + 1] * 6 + r[i + 2]) // 10 for i in range(0, len(r), 9)]
    top = px[0:w * 3]; sky = st.median([(top[i] * 3 + top[i + 1] * 6 + top[i + 2]) // 10 for i in range(0, len(top), 3)])
    return st.pstdev(lum), sum(abs(v - sky) <= 12 for v in lum) / len(lum)
rows = []
for i, l in enumerate(L):
    m = re.match(r"\[fbdump\] n=(\d+) .*stride=(\d+)", l)
    if not m or i < cine: continue
    f = os.path.join(D, "fb", "fb_%07d_w%s.ppm" % (int(m[1]), m[2]))
    if not os.path.exists(f): continue
    rows.append((int(m[1]), "intro" if i < mis else "flight", os.stat(f).st_mtime, *score(f)))
def split(sel, ph, k):
    a = [r[k] for r in sel if int(r[2] + ph) % 2 == 0]; b = [r[k] for r in sel if int(r[2] + ph) % 2 == 1]
    return (st.mean(a) if a else 0, st.mean(b) if b else 0, len(a), len(b))
intro = [r for r in rows if r[1] == "intro"]; fl = [r for r in rows if r[1] == "flight"]
import ctypes, time
lib = ctypes.CDLL(None); lib.mach_absolute_time.restype = ctypes.c_uint64
OFF = time.time() - lib.mach_absolute_time() / 24e6   # wall - mach seconds; constant while the host has not slept since the run
EXACT = "--fit" not in sys.argv
fits = sorted(((abs(split(intro, p / 50, 3)[0] - split(intro, p / 50, 3)[1]), p / 50) for p in range(100)), reverse=True)
ph = fits[0][1] if not EXACT else (-OFF) % 2.0; null = st.median(f[0] for f in fits)
print("phase from mach clock (armB = odd mach second = old cap)" if EXACT else "phase FITTED"); print("dumps intro=%d flight=%d phase=%.2f fitted|d|=%.2f median-phase|d|=%.2f" % (len(intro), len(fl), ph, fits[0][0], null))
for name, sel in (("intro", intro), ("flight", fl)):
    s0, s1, n0, n1 = split(sel, ph, 3); k0, k1, _, _ = split(sel, ph, 4)
    print("%-6s armA n=%d std=%.1f skyfrac=%.3f | armB n=%d std=%.1f skyfrac=%.3f | d_std=%.1f" % (name, n0, s0, k0, n1, s1, k1, s0 - s1))
print("intro swap range %d-%d" % (intro[0][0], intro[-1][0]) if intro else "no intro")
for r in intro[::max(1, len(intro) // 30)]: print("  n=%d arm=%d std=%.1f sky=%.2f" % (r[0], int(r[2] + ph) % 2, r[3], r[4]))
