#!/usr/bin/env python3
"""s7552 class GL scorer: what are the bytes RT64's colour writeback changes OUTSIDE the pair's draw rect (rtOut, s7551)?
Sums [s7552] lines (main.cpp s7551::post, ROGUESQ_S7551_GK=1) with t >= --from (default 72, past the mission load).
Per 16-bit outside pixel unchanged since DL start but changed by the writeback (rtPx), the game build tests post == F(pre, d),
F = RT64's own RGBA16 -> float -> Float4ToRGBA16 requantisation with dither d (FbWriteColorCS + Formats.hlsli):
mPat = d from the fb's bestDitherPattern table at (x, y); mAny = some d in 0..7; mZero = d = 0 (an exact round trip, i.e. no change).
Verdicts: CTL-FAIL (no plant seen/clobbered in [s7551] C lines, or the classifier accepts > 20% of changed DRAWN pixels: inAny/inChg,
so it cannot reject foreign content), NONE (rtPx = 0), H-dither-requant (mAny >= 99% of rtPx: undrawn pixels re-dithered by RT64),
H-rect-edge (>= 90% of rtPx within 1 px of the rect edge), else H-stale-native (foreign/structured content).
--controls: synthetic self-test (must print controls 5/5)."""
import re, sys
KEYS = "outPx rtPx mPat mAny mZero unm alpha up down d1 d2 d3 e0 e1 e2 e4 e16 inChg inAny b4".split()
L52 = re.compile(r"\[s7552\] t=([0-9.]+) ph=(\d+) (.*)")
L51 = re.compile(r"\[s7551\] t=([0-9.]+) ph=\d+ kind=C (.*)")
def score(lines, t0):
    g = {k: 0 for k in KEYS}; wb = [0] * 5; rt = [0] * 5; pl = ps = pc = 0
    for ln in lines:
        m = L52.search(ln)
        if m and float(m.group(1)) >= t0:
            f = dict(kv.split("=") for kv in m.group(3).split())
            for k in KEYS: g[k] += int(f.get(k, 0))
            for i, v in enumerate(f.get("wbPat", "0,0,0,0,0").split(",")): wb[i] += int(v)
            for i, v in enumerate(f.get("rtPat", "0,0,0,0,0").split(",")): rt[i] += int(v)
            continue
        m = L51.search(ln)
        if m and float(m.group(1)) >= t0:
            f = dict(kv.split("=") for kv in m.group(2).split()); pl += int(f["plants"]); ps += int(f["pseen"]); pc += int(f["pclob"])
    ctl_plant = pl > 0 and ps > 0 and pc >= 0.97 * ps
    ctl_rej = g["inChg"] > 0 and g["inAny"] <= 0.20 * g["inChg"]
    n = g["rtPx"]
    if not (ctl_plant and ctl_rej): v = "CTL-FAIL"
    elif n == 0: v = "NONE"
    elif g["mAny"] >= 0.99 * n: v = "H-dither-requant"
    elif g["e0"] + g["e1"] >= 0.90 * n: v = "H-rect-edge"
    else: v = "H-stale-native"
    return v, g, wb, rt, (pl, ps, pc)
def controls():
    mk = lambda t=100.0, **k: f"[s7552] t={t} ph=9 " + " ".join(f"{x}={k.get(x, 0)}" for x in KEYS) + " wbPat=1,0,0,0,0 rtPat=1,0,0,0,0"
    p = "[s7551] t=100.0 ph=9 kind=C plants=2 pseen=8 pclob=8"
    ok = 0
    ok += score([p, mk(rtPx=100, mAny=100, inChg=50, inAny=2)], 72)[0] == "H-dither-requant"
    ok += score([p, mk(rtPx=100, mAny=10, e0=95, inChg=50, inAny=2)], 72)[0] == "H-rect-edge"
    ok += score([p, mk(rtPx=100, mAny=10, e16=95, inChg=50, inAny=2)], 72)[0] == "H-stale-native"
    ok += score([p, mk(rtPx=100, mAny=100, inChg=50, inAny=40)], 72)[0] == "CTL-FAIL"
    ok += score([p.replace("t=100.0", "t=10.0"), mk(rtPx=100, mAny=100, inChg=50, inAny=2)], 72)[0] == "CTL-FAIL"
    print(f"controls {ok}/5"); return 0 if ok == 5 else 1
def main(a):
    if "--controls" in a: return controls()
    t0 = 72.0
    if "--from" in a: i = a.index("--from"); t0 = float(a[i + 1]); del a[i:i + 2]
    rc = 0
    for p in a:
        v, g, wb, rt, pc = score(open(p, errors="replace"), t0)
        n = max(g["rtPx"], 1)
        print(f"{p}: {v} rtPx={g['rtPx']} outPx={g['outPx']} mPat={g['mPat']/n:.4f} mAny={g['mAny']/n:.4f} mZero={g['mZero']} unm={g['unm']} "
              f"up={g['up']} down={g['down']} d1={g['d1']} d2={g['d2']} d3={g['d3']} alpha={g['alpha']} edge0-1={g['e0']+g['e1']} e2={g['e2']} e4={g['e4']} e16={g['e16']} "
              f"inChg={g['inChg']} inAny={g['inAny']} b4={g['b4']} wbPat={wb} rtPat={rt} plant(pl,seen,clob)={pc}")
        if v == "CTL-FAIL": rc = 1
    return rc
if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
