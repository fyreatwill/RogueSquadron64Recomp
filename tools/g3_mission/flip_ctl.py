# positive control (s6769): flip bit 0 of the first rand row with caller SITE at/after file line START, in a copy.
# (s6768 flip_ctl.py also counted 8006c018 xtrace rows, so its N-th row can be one g3_rand_ticks never compares.)
# usage: flip_ctl.py PORT_RAND DST [START=30000] [SITE=80076cf8]
import sys
src, dst = sys.argv[1], sys.argv[2]
start = int(sys.argv[3]) if len(sys.argv) > 3 else 30000
site = sys.argv[4] if len(sys.argv) > 4 else "80076cf8"
L = open(src, errors="replace").readlines()
for i in range(start, len(L)):
    f = L[i].split()
    if len(f) == 4 and f[2] == site:
        f[3] = "%08x" % (int(f[3], 16) ^ 1); print("flipped line", i, L[i].strip(), "->", f[3]); L[i] = " ".join(f) + "\n"; break
open(dst, "w").writelines(L)
