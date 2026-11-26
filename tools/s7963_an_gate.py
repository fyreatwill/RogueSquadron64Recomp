#!/usr/bin/env python3
"""s7963 class AN (App Nap / background throttling / process suspension). e2e tools/s7963_an_e2e.zsh, one run, retained capture
scratch/s7963/an1 (_events.txt, _pring.txt.zst). H-nap (a hidden/occluded window gets napped -> VI/present cadence throttles, then a
catch-up burst = G5c 'buffering') vs H-moot. Measured: hidden 60 s the compositor showed 0 presents (CoreAnimation presentedTime=0, the
positive control that the hide took effect) while the game queued presents at the scene's nominal rate (30/s cinematic, 60/s static,
same as foreground); after SIGSTOP 5 s + SIGCONT no 1-s bucket exceeded nominal (no catch-up burst). Mechanism (second line):
SDL_DisableScreenSaver (SDL default) holds a PreventUserIdleDisplaySleep IOPMAssertion for the pid, and the exe is unbundled
(lsappinfo bundleID NULL), so App Nap does not apply. Selects H-moot; class closed with no code change.
STATIC: host code must not re-enable the screensaver (drops the assertion) and CMake must not bundle the exe (App Nap applies to bundles).
MUTANT: planting SDL_EnableScreenSaver() into a copy of main.cpp must be caught."""
import os, re, subprocess, sys, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rs64_zopen import zopen
root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
pfx = sys.argv[1] if len(sys.argv) > 1 else os.path.join(root, "scratch/s7963/an1")
BAD = re.compile(r"SDL_EnableScreenSaver\s*\(|SDL_HINT_VIDEO_ALLOW_SCREENSAVER|\"SDL_VIDEO_ALLOW_SCREENSAVER\"|MACOSX_BUNDLE")
srcs = {f: open(f, errors="replace").read() for d in ("src/main", "src/rsp", "lib/N64ModernRuntime/librecomp/src", "lib/N64ModernRuntime/ultramodern/src")
        for f in glob.glob(os.path.join(root, d, "*.cpp"))}
srcs["CMakeLists.txt"] = open(os.path.join(root, "CMakeLists.txt")).read()
hits = [f for f, s in srcs.items() if BAD.search(s)]
m = os.path.join(root, "src/main/main.cpp"); mut = srcs[m].replace("int main(", "static void rs64_m(){SDL_EnableScreenSaver();}\nint main(", 1)
mb = 1 if BAD.search(mut) and mut != srcs[m] else 0
print(f"STATIC bad_sites={len(hits)} {' '.join(os.path.relpath(h, root) for h in hits)} {'PASS' if not hits else 'FAIL'}")
print(f"MUTANT planted_bad={mb} {'PASS' if mb else 'FAIL'}")
ev = {}
for l in zopen(pfx + "_events.txt"):
    p = l.split()
    if len(p) > 2 and p[1] == "phase": ev[p[2]] = float(p[0])
Q, P = [], {}
for l in zopen(pfx + "_pring.txt"):
    if l[:2] == "Q " and l.endswith("\n"):
        mt = re.search(r" mtl=(\d+)", l); vi = re.search(r" vi=(\S+)", l); Q.append((float(l.split()[1]), int(mt[1]), vi[1]))
    elif l[:2] == "P ":
        x = re.match(r"P \S+ mtl=(\d+) at=(\S+)", l)
        if x: P[int(x[1])] = float(x[2])
def on(a, b):
    ids = [i for t, i, _ in Q if a <= t < b and i in P]; return len(ids), sum(1 for i in ids if P[i] > 0)
def rate(a, b): return sum(1 for t, _, _ in Q if a <= t < b) / (b - a)
def newr(a, b):
    n, prev = 0, None
    for t, _, v in Q:
        if a <= t < b and prev is not None and v != prev: n += 1
        if t < b: prev = v
    return n / (b - a)
fn, fo = on(ev["fg0"] + 5, ev["hidden"]); hn, ho = on(ev["hidden"] + 2, ev["shown"])
print(f"CONTROL fg_onscreen={fo}/{fn} hidden_onscreen={ho}/{hn} {'PASS' if fn > 500 and fo == fn and hn > 500 and ho == 0 else 'FAIL'}")
hb = [rate(ev["hidden"] + 5 * k, ev["hidden"] + 5 * k + 5) for k in range(int((ev["shown"] - ev["hidden"]) // 5))]
fb = [rate(ev["fg0"] + 5 * k, ev["fg0"] + 5 * k + 5) for k in range(int((ev["hidden"] - ev["fg0"]) // 5))]
print(f"HIDDEN queued/s per 5s min={min(hb):.1f} max={max(hb):.1f} (fg min={min(fb):.1f} max={max(fb):.1f}) {'PASS' if min(hb) >= 28 and max(hb) <= 63 else 'FAIL'}")
stp = rate(ev["stop"] + 0.2, ev["cont"])
rb = [(rate(ev["cont"] + k, ev["cont"] + k + 1), newr(ev["cont"] + k, ev["cont"] + k + 1)) for k in range(15)]
mq, mn = max(r[0] for r in rb), max(r[1] for r in rb)
print(f"RESUME stopped_queued/s={stp:.1f} max_1s_queued/s={mq:.0f} max_1s_new/s={mn:.0f} {'PASS' if stp < 1 and mq <= 66 and mn <= 33 else 'FAIL'}")
print("VERDICT CLOSED (H-moot)" if not hits and mb and fo == fn and ho == 0 and min(hb) >= 28 and mq <= 66 and mn <= 33 else "VERDICT OPEN")
