#!/usr/bin/env python3
"""s6754 G3: attribute every guest rand() call to its runInMissionFrame tick (0x800FA730 xtrace row with pin=) in a
dt-pinned retail/port pair, and report the first call whose (tick, caller, value) differs. g3_rand_align.py keys calls
by each arm's own clock (retail VI, port us), which cannot say whether a mismatch is a sim divergence or just a
different tick; this keys them by sim tick. usage: g3_rand_ticks.py RETAIL_ORACLE_LOG PORT_RAND_TXT [context]"""
import os, sys

RAND, TICK = 0x80003430, int(os.environ.get("G3_TICK", "800FA730"), 16)  # s6771: G3_TICK=<hex pc> picks the tick row (800C6674 = race frame, advanceWrappingPhaseAccumulator)
SKIP = {0x8006BEC8, 0x8006C018, 0x8006C010, 0x800AF374, 0x800C6674, TICK,
        0x8008EE08, 0x8008EE84}  # s6757: s6755 AI-buffer marker rows (osAiSetNextBuffer jal sites)

def walk(path, retail):
    tick, out = -1, []
    for l in open(path, errors="replace"):
        if retail:
            if not l.startswith("[xtrace] "):
                continue
            f = l.split()[1:]
        else:
            f = l.split()
        if len(f) < 4:
            continue
        try:
            site = int(f[2], 16)
        except ValueError:
            continue
        if retail and len(f) >= 7:
            pc = int(f[4][3:], 16)
            if pc == TICK:
                tick += 1
                continue
            if pc != RAND:
                continue
            site -= 8  # retail logs $ra = jal+8, the port the jal itself
        elif not retail:
            pin = any(x.startswith("pin=") for x in f[4:])
            if site == TICK and pin:
                tick += 1
                continue
            if site in SKIP or pin or any(x.startswith("m=") for x in f[4:]):
                continue
        out.append((tick, site, int(f[3], 16)))
    return out

r, p = walk(sys.argv[1], True), walk(sys.argv[2], False)
# s6771: G3_MIN_TICK=0 drops calls before the first tick (a one-shot rngSeed poke on tick 0 makes them arm-specific)
MIN = int(os.environ.get("G3_MIN_TICK", "-1"))
r, p = [x for x in r if x[0] >= MIN], [x for x in p if x[0] >= MIN]
ctx = int(sys.argv[3]) if len(sys.argv) > 3 else 8
n = min(len(r), len(p))
bad = next((i for i in range(n) if r[i] != p[i]), None)
print("retail calls %d (ticks %d)  port calls %d (ticks %d)  compared %d" % (
    len(r), r[-1][0] + 1 if r else 0, len(p), p[-1][0] + 1 if p else 0, n))
print("first (tick, caller, value) mismatch at index", bad)
if bad is not None:
    for i in range(max(0, bad - ctx), min(n, bad + ctx)):
        a, b = r[i], p[i]
        print("%s %6d  R t%-5d %08x %08x | P t%-5d %08x %08x" % ("!=" if a != b else "  ", i, *a, *b))
