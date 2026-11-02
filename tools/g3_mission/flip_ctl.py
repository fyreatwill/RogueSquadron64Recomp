# positive control (s6769): flip bit 0 of the first rand row with caller SITE at/after file line START, in a copy.
# (s6768 flip_ctl.py also counted 8006c018 xtrace rows, so its N-th row can be one g3_rand_ticks never compares.)
# usage: flip_ctl.py PORT_RAND DST [START=30000] [SITE]
# s6771: no SITE = the first rand row g3_rand_ticks compares (the mission-17 race never calls 80076cf8: 0 flips, dead control)
import os, sys
src, dst = sys.argv[1], sys.argv[2]
start = int(sys.argv[3]) if len(sys.argv) > 3 else 30000
site = sys.argv[4] if len(sys.argv) > 4 else None
NOCMP = {"8006bec8", "8006c018", "8006c010", "800af374", "800c6674", "800fa730", "8008ee08", "8008ee84"}
L = open(src, errors="replace").readlines()
start = min(start, len(L) // 2)  # s6771: short traces (the mission-17 race is 458 ticks)
# s6772: rows before the first tick row are dropped by G3_MIN_TICK=0; the mission-18 trace's first 800fa730 row is at
# line 30941, so START=30000 flipped a level-select row and the control silently tested nothing. Start at the first tick.
tk = os.environ.get("G3_TICK", "800FA730").lower()
start = max(start, next((i for i, l in enumerate(L) if l.split()[2:3] == [tk]), 0))
for i in range(start, len(L)):
    f = L[i].split()
    if len(f) == 4 and (f[2] == site if site else f[2] not in NOCMP):
        f[3] = "%08x" % (int(f[3], 16) ^ 1); print("flipped line", i, L[i].strip(), "->", f[3]); L[i] = " ".join(f) + "\n"; break
else:
    sys.exit("flip_ctl: no row to flip (dead control)")
open(dst, "w").writelines(L)
