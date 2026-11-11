#!/usr/bin/env python3
"""s7121 fps60-cam-step: classify the one-tick 2-16 u presented-eye steps found by s7119_hop --lag (open flight, no need/lift).

Per flight-cam tick (nl+rx joined, as s7119_hop) we also attach the nearest preceding ch line of the same cam (chase: pos, tgt=look
target, dist, dt) and note every OTHER cam id that logs rx/pe lines within +-0.25 s (cutscene / alt cams).
Event = |d2Y| > THR with need==0 and lift==0 on all 4 window ticks (same as s7119 class 'neither').
Classes:
  H-cut  : X or Z also jumps (|d2X| or |d2Z| > THR) or tgt jumps (|d2 tgt| > THR) or another cam is active nearby or a seg gap.
  H-snap : Y-only step, chase tgt smooth (|d2 tgt| < THR/4).
  H-log  : the step vanishes when Y is taken from the next tick's ch.pos (the chase input = this tick's rx pos), i.e. rx/ch disagree.
NOTE (s7121): s7119_hop joined nl+rx across ALL cam ids; 19/21 of its open-flight 2-16 u "steps" were windows spanning a switch
between camera objects 80138458 (flight) and 80138A28/80138930. Filter by cam (here, or s7119_hop --cam 80138458).
Positive control: --inject T:U adds U to rx Y of flight tick T only (X/Z/tgt untouched) -> must classify as H-snap.
"""
import re, argparse
ap = argparse.ArgumentParser(); ap.add_argument("push", nargs="+"); ap.add_argument("--thr", type=float, default=0.5)
ap.add_argument("--inject", default=None); ap.add_argument("--inject-chase", action="store_true", help="also put the step into the next tick's ch.pos (a real step the chase consumes) -> must read H-snap; without it -> H-log"); ap.add_argument("--show", type=int, default=3)
a = ap.parse_args()
N = r"(-?[0-9.eE+-]+)"; V = N + "," + N + "," + N
rx_re = re.compile(r"^rx m=(\d+) cam=([0-9A-F]+) .* pos=" + V)
nl_re = re.compile(r"^nl m=(\d+) cam=([0-9A-F]+) on=(\d)(?: k=([0-9.]+))? need=" + N + " lift=" + N)
ch_re = re.compile(r"^ch m=(\d+) lim=(\d+) fc=(\d+) cam=([0-9A-F]+) dist=" + N + " dt=" + N + " pos=" + V + " tgt=" + V)
any_re = re.compile(r"^(rx|pe|ch|pc) m=(\d+) cam=([0-9A-F]+)")
FL = "80138458"
tot = {}
for path in a.push:
    ticks, other, pend, lastch = [], [], None, None
    for ln in open(path, errors="replace"):
        g = any_re.match(ln)
        if g and g.group(3) != FL: other.append((int(g.group(2)), g.group(3)))
        if ln.startswith("ch "):
            mm = ch_re.match(ln)
            if mm and mm.group(4) == FL: lastch = mm
        elif ln.startswith("nl "):
            mm = nl_re.match(ln); pend = mm if mm and mm.group(2) == FL else None
        elif ln.startswith("rx ") and pend is not None:
            mm = rx_re.match(ln)
            if mm and mm.group(2) == FL:
                c = lastch
                ticks.append(dict(m=int(mm.group(1)), p=[float(mm.group(i)) for i in (3, 4, 5)],
                    need=float(pend.group(5)), lift=float(pend.group(6)), on=int(pend.group(3)),
                    cp=[float(c.group(i)) for i in (7, 8, 9)] if c else None, tg=[float(c.group(i)) for i in (10, 11, 12)] if c else None,
                    dist=float(c.group(5)) if c else 0, dt=float(c.group(6)) if c else 0, chm=int(c.group(1)) if c else 0))
            pend = None
    if a.inject:
        t, u = a.inject.split(":"); ticks[int(t)]["p"][1] += float(u); print(f"inject tick {t} m={ticks[int(t)]['m']} Y+={u}")
        if a.inject_chase and ticks[int(t) + 1]["cp"]: ticks[int(t) + 1]["cp"] = list(ticks[int(t) + 1]["cp"]); ticks[int(t) + 1]["cp"][1] += float(u)
    other.sort(); om = [x[0] for x in other]
    import bisect
    def near_other(m):
        i = bisect.bisect_left(om, m - 6_000_000); s = set()
        while i < len(om) and om[i] <= m + 6_000_000: s.add(other[i][1]); i += 1
        return s
    def d2(w, f, k): 
        v = [f(x) for x in w]
        if any(q is None for q in v): return 0.0
        return abs(v[3][k] - 2 * v[2][k] + v[1][k])
    C = {}; shown = 0; nt = 0
    print(f"== {path}: flight ticks {len(ticks)}, other-cam lines {len(other)}")
    for i in range(3, len(ticks)):
        w = ticks[i - 3:i + 1]
        if w[3]["m"] - w[0]["m"] > 3 * 960_000: continue
        nt += 1
        dy = d2(w, lambda x: x["p"], 1)
        if dy <= a.thr or any(x["need"] > 0 or x["lift"] > 0 for x in w): continue
        dx, dz = d2(w, lambda x: x["p"], 0), d2(w, lambda x: x["p"], 2)
        tgm = max(d2(w, lambda x: x["tg"], k) for k in range(3))
        # ch.pos on tick t is the PREVIOUS tick's rx pos (chase input), so the witness for rx tick t is ch of tick t+1
        cy = d2(ticks[i - 2:i + 2], lambda x: x["cp"], 1) if i + 1 < len(ticks) else 0.0
        oc = near_other(w[3]["m"])
        gap = (w[3]["m"] - w[2]["m"]) / 24e6
        if dx > a.thr or dz > a.thr or tgm > a.thr or oc: cls = "H-cut"
        elif cy < dy / 4: cls = "H-log"
        elif tgm < a.thr / 4: cls = "H-snap"
        else: cls = "mixed"
        C[cls] = C.get(cls, 0) + 1
        print(f"  ev m={w[3]['m']} on={w[3]['on']} d2Y {dy:.2f} d2X {dx:.2f} d2Z {dz:.2f} d2tgt {tgm:.2f} d2chY {cy:.2f} dt {w[3]['dt']:.4f} "
              f"dist {w[2]['dist']:.2f}->{w[3]['dist']:.2f} gap {gap*1e3:.1f}ms other {sorted(oc)} -> {cls}")
        if shown < a.show:
            shown += 1
            for x in ticks[max(0, i - 4):i + 2]:
                print(f"      m={x['m']} pos={x['p'][0]:.2f},{x['p'][1]:.2f},{x['p'][2]:.2f} ch={x['cp'] and ','.join(f'{q:.2f}' for q in x['cp'])} "
                      f"tgt={x['tg'] and ','.join(f'{q:.2f}' for q in x['tg'])} dist={x['dist']:.2f} dt={x['dt']:.4f}")
    print(f"  ticks scored {nt}  classes {C}")
    for k, v in C.items(): tot[k] = tot.get(k, 0) + v
print("POOLED", tot)
