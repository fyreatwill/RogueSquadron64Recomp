#!/usr/bin/env python3
"""s5851: min player->target distance (x,z plane and 3D) for each lv0 class-1 descriptor, killed vs survivor.
Inputs: run log with [plpos] lines (ROGUESQ_LOG_PLPOS=1), [spawn1] and [ctr1] lines. usage: analyze_lv0_player_vs_targets.py RUN.LOG"""
import re, struct, sys, math
import os as _os; sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__))); from rs64_zopen import zopen, zbytes  # s7805: zst-only retained inputs
seen, killed, pl = {}, set(), []
for l in zopen(sys.argv[1], errors="replace"):
    m = re.match(r"\[spawn1\] #\d+ desc=0x(\w+) npc=0x\w+ id=0x(\w+) w=(.*)", l)
    if m: seen.setdefault(m.group(1), (int(m.group(2), 16), [int(x, 16) for x in m.group(3).split()]))
    m = re.match(r"\[ctr1\] set #\d+ id=0x(\w+) val=1 a2=1", l)
    if m: killed.add(int(m.group(1), 16))
    m = re.match(r"\[plpos\] el=([\d.]+) .*pos=\(([-\d.]+),([-\d.]+),([-\d.]+)\)", l)
    if m: pl.append(tuple(float(x) for x in m.groups()))
fl = lambda w: struct.unpack(">f", struct.pack(">I", w))[0]
xs = [p[1] for p in pl]; zs = [p[3] for p in pl]
print("plpos samples=%d x[%.0f..%.0f] z[%.0f..%.0f] end=(%.0f,%.0f)" % (len(pl), min(xs), max(xs), min(zs), max(zs), xs[-1], zs[-1]))
print("id    K  tx ty tz   min_xz  min_3d  at_el")
rows = []
for d, (i, w) in seen.items():
    t = [fl(w[4]), fl(w[5]), fl(w[6])]
    best = min(((math.hypot(p[1]-t[0], p[3]-t[2]), math.dist(p[1:], t), p[0]) for p in pl))
    rows.append((i, i in killed, t, best))
for i, k, t, b in sorted(rows):
    print("%#4x  %s  %4.0f %3.0f %4.0f  %6.1f  %6.1f  %6.0f" % (i, "K" if k else "-", *t, b[0], b[1], b[2]))
for name, sel in (("killed", True), ("survivor", False)):
    v = [b[0] for i, k, t, b in rows if k == sel]
    print(name, len(v), "min_xz median %.1f max %.1f min %.1f" % (sorted(v)[len(v)//2], max(v), min(v)))
# s5851: button state while within R of each target (fire exposure)
R = float(sys.argv[2]) if len(sys.argv) > 2 else 15.0
btn = [int(re.search(r"btn=0x(\w+)", l).group(1), 16) for l in zopen(sys.argv[1], errors="replace") if l.startswith("[plpos]")]
print("in-range(<%g xz) samples and samples with each button bit; B=0x4000 A=0x8000" % R)
for d, (i, w) in sorted(seen.items(), key=lambda x: x[1][0]):
    tx, tz = fl(w[4]), fl(w[6])
    ix = [j for j, p in enumerate(pl) if math.hypot(p[1]-tx, p[3]-tz) < R]
    c = lambda m: sum(1 for j in ix if btn[j] & m)
    print("%#4x %s in=%3d A=%3d B=%3d" % (i, "K" if i in killed else "-", len(ix), c(0x8000), c(0x4000)))
