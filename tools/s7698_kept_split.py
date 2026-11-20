#!/usr/bin/env python3
"""s7698 positive control for the POOLMIN toggle: G3E trace site-4 kept nodes per streamTerrainGridCellsByDistance call, for calls
under the cutscene pool (cap field == 4096), split by mach-second parity (odd = old cap). Swap -> wall time from fb dump mtimes
(interpolated), wall -> mach via the current offset (valid while the host has not slept). Intro only (swaps between the level cineBody call and the mission poolx line). Usage: s7698_kept_split.py <run dir> <level>"""
import sys, os, re, bisect, ctypes, time, statistics as st
D = sys.argv[1]; lib = ctypes.CDLL(None); lib.mach_absolute_time.restype = ctypes.c_uint64
OFF = time.time() - lib.mach_absolute_time() / 24e6
pts = []
for f in sorted(os.listdir(D + "/fb")):
    m = re.match(r"fb_(\d+)_w", f)
    if m: pts.append((int(m[1]), os.stat(D + "/fb/" + f).st_mtime - OFF))
sw = [p[0] for p in pts]
L = open(D + "/run.log", errors="replace").read().splitlines(); LV = int(sys.argv[2])
cine = next(i for i, l in enumerate(L) if (("[poolx] cap" in l and "-> 4096" in l) if LV < 0 else ("[cineBody] call#" in l and re.search(r"a0=0x0*%X " % LV, l))))   # s7700: LV<0 = AT THE MOVIES, range from the first cutscene-pool cap
mis = len(L) if LV < 0 else next((i for i, l in enumerate(L) if i > cine and "[poolx] cap 2048" in l), len(L))   # s7699: no flight line = intro ran to the kill (L5)
ns = [int(m[1]) for l in L[cine:mis] for m in [re.match(r"\[fbdump\] n=(\d+) ", l)] if m]; S0, S1 = ns[0], ns[-1]
def t(s):
    i = bisect.bisect_left(sw, s)
    if i <= 0 or i >= len(pts): return None
    (s0, t0), (s1, t1) = pts[i - 1], pts[i]; return t0 + (t1 - t0) * (s - s0) / (s1 - s0)
arm = {0: [], 1: []}; win = {0: [], 1: []}; edge = 0
for l in open(D + "/g3e.txt"):
    v = l.split()
    if len(v) < 6 or v[2] != "4" or v[5] != "4096": continue   # s7700: SIGKILL truncates the last trace line
    if not S0 <= int(v[1]) <= S1: continue
    tt = t(int(v[1]))
    if tt is None: continue
    if abs(tt - round(tt)) < 0.12: edge += 1; continue   # drop calls within 0.12 s of a flip (interpolation + lag)
    p = int(tt) & 1; arm[p].append(int(v[3])); win[p].append(int(v[4]))
for p, nm in ((0, "even=floor 4096"), (1, "odd=old cap")):
    a = arm[p]; print("%-16s calls=%d kept p50=%s mean=%.0f max=%s window p50=%s" % (nm, len(a), st.median(a) if a else "-", st.mean(a) if a else 0, max(a) if a else "-", st.median(win[p]) if a else "-"))
print("intro swaps %d-%d, dropped near flips: %d" % (S0, S1, edge))
