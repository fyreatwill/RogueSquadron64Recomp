#!/usr/bin/env python3
"""s7551 class GK scorer: RT64 writeback vs guest/host changes made to a span between checkRDRAM (DL start) and the writeback.
usage: s7551_gk_score.py <log> [<log>...] [--from SECONDS]   (sums [s7551] window lines with t >= from; default 72 = past the mission load)
Verdicts per log: CTL-FAIL (no plant seen, or fewer than 97% of seen plant bytes clobbered), H-clean (0 non-plant changed bytes),
H-clobber-benign-candidate (changed bytes but 0 clobbered), H-clobber (changed bytes replaced by the writeback).
--controls: self-test on synthetic lines (must print controls 4/4)."""
import re, sys
KEYS = "checks wb nosnap bytes gwb gch gchIn gchOut cwb clob clobIn clobOut revert rtOut plants pseen pclob".split()
LINE = re.compile(r"\[s7551\] t=([0-9.]+) ph=(\d+) kind=([CZ]) (.*)")
def score(lines, t0):
    tot = {k: {x: 0 for x in KEYS} for k in "CZ"}; ev = 0
    for ln in lines:
        if "[s7551-ev]" in ln: ev += 1; continue
        m = LINE.search(ln)
        if not m or float(m.group(1)) < t0: continue
        f = dict(kv.split("=") for kv in m.group(4).split())
        for x in KEYS:
            if x in f: tot[m.group(3)][x] += int(f[x])
    c, z = tot["C"], tot["Z"]
    pseen = c["pseen"] + z["pseen"]; pclob = c["pclob"] + z["pclob"]
    if c["plants"] == 0 or pseen == 0 or pclob < 0.97 * pseen: v = "CTL-FAIL"  # drawn plant pixels can redraw to the planted byte (1/256)
    elif c["clob"] + z["clob"]: v = "H-clobber"
    elif c["gch"] + z["gch"]: v = "H-clobber-benign-candidate"
    else: v = "H-clean"
    return v, tot, ev
def controls():
    ok = 0
    mk = lambda **k: "[s7551] t=100.0 ph=9 kind=C " + " ".join(f"{x}={k.get(x,0)}" for x in KEYS)
    ok += score([mk(wb=5, bytes=10, plants=2, pseen=8, pclob=8)], 72)[0] == "H-clean"
    ok += score([mk(wb=5, plants=2, pseen=8, pclob=8, gch=3, clob=1)], 72)[0] == "H-clobber"
    ok += score([mk(wb=5, plants=2, pseen=8, pclob=7)], 72)[0] == "CTL-FAIL"
    ok += score([mk(wb=5, plants=2, pseen=8, pclob=8, gch=3).replace("t=100.0", "t=10.0")], 72)[0] == "CTL-FAIL"
    print(f"controls {ok}/4"); return 0 if ok == 4 else 1
def main(a):
    if "--controls" in a: return controls()
    t0 = 72.0
    if "--from" in a: i = a.index("--from"); t0 = float(a[i + 1]); del a[i:i + 2]
    rc = 0
    for p in a:
        v, tot, ev = score(open(p, errors="replace"), t0)
        for k in "CZ":
            print(f"{p} kind={k} " + " ".join(f"{x}={tot[k][x]}" for x in KEYS))
        print(f"{p} verdict={v} events={ev}")
        rc |= v == "CTL-FAIL"
    return rc
sys.exit(main(sys.argv[1:]))
