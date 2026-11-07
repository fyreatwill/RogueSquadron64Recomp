#!/usr/bin/env python3
"""s6932 G1e: ten generated scheduler/submit probes (s3290-s3311) throttle or skip on `width < 640u`, written when width >= 640 meant the anomalous
cinematic state. ORIGIN: ours. Wide aspect keeps the committed VI width >= 640 for the whole game, so at 16:9 and 21:9 every event printed and flushed
on the game and scheduler threads, with no logging env set: 1.5M lines, 223 MB in a 300 s dd4 16:9 run.
Each test becomes (width < 640u || rs64_s6932_quiet()), so wide logs at the 4:3 rate. rs64_s6932_quiet (main.cpp): default quiet unless probes are on,
ROGUESQ_WIDE_LOGQUIET=0 old, =tog 10 s blocks on CLOCK_UPTIME_RAW, the present ring's clock (odd block quiet).
Runs last in RS64_REPLAY. Idempotent.  Usage: apply_s6932_widequiet.py [RecompiledFuncs dir]"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s6932 widequiet"
OLD = "width < 640u"
NEW = "(width < 640u || rs64_s6932_quiet())"
DECL = "extern int rs64_s6932_quiet(void); /* " + TAG + " */\n"
n = 0
for f in sorted(D.glob("funcs_*.c")):
    t = f.read_text(errors="surrogateescape")
    if TAG in t:
        print("already applied", f.name); continue
    c = t.count(OLD)
    if not c: continue
    a = t.find("RECOMP_FUNC "); s = t.find("static ")
    a = min(x for x in (a, s) if x >= 0)
    t = t[:a] + DECL + t[a:].replace(OLD, NEW)
    f.write_text(t, errors="surrogateescape"); n += c; print("applied", f.name, c)
print("sites", n)
