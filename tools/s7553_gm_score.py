#!/usr/bin/env python3
"""s7553 class GM scorer: what are the bytes RT64's writeback changes OUTSIDE the pair's draw rect (rtPx) in ANY phase?
Sums [s7553] lines (main.cpp s7551::post GM block, ROGUESQ_S7551_GK=1 + _PLANT=1) per kind. Per rtPx pixel (outside the rect,
unchanged since DL start, changed by the writeback) the game build records: rawIn = column inside the pair's union of every draw rect
BEFORE the scissor (rs64RawRect, RT64 rdp/rsp merge sites), scIn = inside the scissor union, preIsLast = RAM before the writeback
equals the last value RT64 itself wrote back at that address (16 MB per-byte shadow, any geometry/kind), near1 = post within 1 per
channel of that value (colour), zSameZ = post>>2 == pre>>2 (depth: z field kept, only the 2-bit dz changes).
Verdicts per kind: CTL-FAIL (plants not seen/clobbered >= 97%), NONE, C: H-dither (preIsLast and near1 >= 99.5%: RT64 re-dithers its
own earlier output from the retained target), Z: H-depth-req (preIsLast and zSameZ >= 99.5%), else H-foreign.
--controls: synthetic self-test (must print controls 5/5)."""
import re, sys, collections
L53 = re.compile(r"\[s7553\] t=([0-9.]+) ph=(\d+) kind=(\w) (.*)")
L51 = re.compile(r"\[s7551\] t=([0-9.]+) ph=\d+ kind=\w (.*)")
def score(lines, t0):
    g = {"C": collections.Counter(), "Z": collections.Counter()}; pl = ps = pc = 0
    for ln in lines:
        m = L53.search(ln)
        if m and float(m.group(1)) >= t0:
            g[m.group(3)].update({k: int(v) for k, v in (kv.split("=") for kv in m.group(4).split())}); continue
        m = L51.search(ln)
        if m and float(m.group(1)) >= t0:
            f = dict(kv.split("=") for kv in m.group(2).split()); pl += int(f["plants"]); ps += int(f["pseen"]); pc += int(f["pclob"])
    ctl = pl > 0 and ps > 0 and pc >= 0.97 * ps
    out = {}
    for k, c in g.items():
        n = c["rt"]
        if not ctl: v = "CTL-FAIL"
        elif n == 0: v = "NONE"
        elif k == "C" and c["preIsLast"] >= 0.995 * n and c["near1"] >= 0.995 * n: v = "H-dither"
        elif k == "Z" and c["preIsLast"] >= 0.995 * n and c["zSameZ"] >= 0.995 * n: v = "H-depth-req"
        else: v = "H-foreign"
        out[k] = (v, c)
    return out, (pl, ps, pc)
def controls():
    p = "[s7551] t=1.0 ph=3 kind=C plants=2 pseen=8 pclob=8"
    mk = lambda k, **f: f"[s7553] t=1.0 ph=3 kind={k} " + " ".join(f"{a}={b}" for a, b in f.items())
    ok = 0
    ok += score([p, mk("C", rt=100, preIsLast=100, near1=100)], 0)[0]["C"][0] == "H-dither"
    ok += score([p, mk("C", rt=100, preIsLast=100, near1=50)], 0)[0]["C"][0] == "H-foreign"
    ok += score([p, mk("Z", rt=100, preIsLast=100, zSameZ=100)], 0)[0]["Z"][0] == "H-depth-req"
    ok += score([p, mk("Z", rt=100, preIsLast=60, zSameZ=100)], 0)[0]["Z"][0] == "H-foreign"
    ok += score([p.replace("pclob=8", "pclob=1"), mk("C", rt=100, preIsLast=100, near1=100)], 0)[0]["C"][0] == "CTL-FAIL"
    print(f"controls {ok}/5"); return 0 if ok == 5 else 1
def main(a):
    if "--controls" in a: return controls()
    t0 = 0.0
    if "--from" in a: i = a.index("--from"); t0 = float(a[i + 1]); del a[i:i + 2]
    rc = 0
    for p in a:
        out, pc = score(open(p, errors="replace"), t0)
        for k, (v, c) in out.items():
            n = max(c["rt"], 1)
            print(f"{p} {k}: {v} rt={c['rt']} rawIn={c['rawIn']/n:.4f} scIn={c['scIn']/n:.4f} preIsLast={c['preIsLast']/n:.5f} near1={c['near1']/n:.5f} "
                  f"zSameZ={c['zSameZ']/n:.5f} dark={c['dark']} bright={c['bright']} zd1={c['zd1']} zd4={c['zd4']} zd64={c['zd64']} zbig={c['zbig']} wchg={c['wchg']} plant={pc}")
            if v in ("CTL-FAIL", "H-foreign"): rc = 1
    return rc
if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
