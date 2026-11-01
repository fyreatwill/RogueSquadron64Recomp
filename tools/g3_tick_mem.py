#!/usr/bin/env python3
"""s6755 G3: per-sim-tick transitions of an XTRACE_MEM dump block in a dt-pinned retail/port pair.
Both arms dump guest words on the runInMissionFrame tick row (0x800FA730) with RS64_XTRACE_MEM / ROGUESQ_XTRACE_MEM
spec 800FA730:0:<ADDR>:<N>. Prints, per arm, every tick at which any word of the block changes (word offset,
old -> new), then the first tick where the two arms' blocks differ. Sim ticks, not VI/us, are the join key.
usage: g3_tick_mem.py RETAIL_ORACLE_LOG PORT_RAND_TXT ADDR [ADDR...]   (ADDR hex, e.g. 801375d8)
s6755: G3_FROM=<tick> / G3_TO=<tick> limit the printed transitions to a tick window; each transition row also shows
the arm's VI count at that tick; G3_IGN=<hex offs,...> drops per-tick accumulator words (e.g. 04,0c,18) (retail mupen VI vs port host VI), so audio-clocked events can be timed in VI."""
import os
import sys

TICK = "800fa730"

VI = {}

def blocks(path, retail, key):
    tick, out, vi = -1, {}, VI.setdefault(path, {})
    for l in open(path, errors="replace"):
        if retail:
            if not l.startswith("[xtrace] "):
                continue
            f = l.split()
            if len(f) < 6 or f[5] != "pc=" + TICK:
                continue
        else:
            f = l.split()
            if len(f) < 3 or f[2] != TICK:
                continue
        tick += 1
        vi[tick] = int(f[2] if retail else f[1])
        i = l.find(" m=" + key + ":")
        if i >= 0:
            out[tick] = l[i + len(key) + 4:].split()[0].split(",")
    return out

def transitions(b):
    prev, rows = None, []
    for t in sorted(b):
        v = b[t]
        if prev is not None and v != prev:
            rows.append((t, [(4 * i, prev[i], v[i]) for i in range(min(len(v), len(prev))) if v[i] != prev[i]]))
        prev = v
    return rows

def main():
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    for key in (a.lower().removeprefix("0x") for a in sys.argv[3:]):
        r, p = blocks(sys.argv[1], True, key), blocks(sys.argv[2], False, key)
        print(f"== {key}: retail ticks {len(r)}  port ticks {len(p)}")
        lo, hi = int(os.environ.get("G3_FROM", 0)), int(os.environ.get("G3_TO", 1 << 30))
        for name, b, path in (("R", r, sys.argv[1]), ("P", p, sys.argv[2])):
            ign = {int(x, 16) for x in os.environ.get("G3_IGN", "").split(",") if x}
            tr = [(t, [x for x in d if x[0] not in ign]) for t, d in transitions(b) if lo <= t <= hi]
            tr = [(t, d) for t, d in tr if d]
            for t, d in tr[:60]:
                print(f"  {name} t{t:5d} vi{VI[path].get(t, -1):6d} " + " ".join(f"+{o:02x}:{a}->{c}" for o, a, c in d[:8]))
            if len(tr) > 60:
                print(f"  {name} ... {len(tr) - 60} more transitions")
        diff = [t for t in sorted(set(r) & set(p)) if r[t] != p[t]]
        print(f"  first arm diff tick: {diff[0] if diff else None}")

main()
