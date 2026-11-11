#!/usr/bin/env python3
"""s7119 fps60-wall-hop: does the s7115 near-pyramid lift make the presented camera hop / shake more than the
retail near-wall camera does?

Input: ROGUESQ_S7101_CHASE push logs. nl precedes rx for the same cam (flight cam 80138458):
  m = mach_absolute_time (24 MHz). Y = rx pos.y (presented eye y, lift already applied; y points down), lift/need/on/k from the nl line.
The lift is written into the camera state, so the next tick's chase starts from the lifted eye: a lift "offset" is
not an eye drop. What the viewer sees is the presented eye trajectory, so the metrics are on Y:
  jerk  = |d2Y| = |Y[t] - 2Y[t-1] + Y[t-2]|  per tick
  alt   = fraction of consecutive d2Y pairs that flip sign (shake signature), 4-tick windows
Buckets (on, k), whole window in one arm. "wall" = need > 0 on t or t-1 (eye inside the near pyramid; the lift
would act). Fair comparator: wall ticks with on=0 (tog1 runs: same run, retail camera at the same kind of walls).
"free" = need == 0 over the window (open flight).
Pre-registered (NEXT.md s7119): H-hop if on-wall jerk p99 > 1.5x off-wall jerk p99 (same run); H-shake if on-wall
sign-alt rate > 1.5x off-wall with >= 30 windows; else H-smooth. Positive control: --inject T:U adds U to presented
Y of tick T (and marks it wall); the hop counter (jerk > off-wall p99) must rise by >= 2 (t and t+1).
--top N lists the N largest on-wall jerks (one per second) with mach m for the owner sheet.
"""
import re, argparse

ap = argparse.ArgumentParser()
ap.add_argument("push", nargs="+")
ap.add_argument("--inject", default=None)
ap.add_argument("--edge", type=float, default=0.0, help="skip windows < EDGE s after an arm change")
ap.add_argument("--top", type=int, default=0)
ap.add_argument("--cam", default=None, help="s7121: keep only this cam id (e.g. 80138458 = flight cam); default mixes all cams (s7119/s7120 behaviour, which joins across cam switches)")
ap.add_argument("--lag", action="store_true", help="s7120: for >0.5 'neither' events print ticks since last need>0 / lift>0 (same arm segment)")
a = ap.parse_args()

NUM = r"(-?[0-9.eE+-]+)"
rx_re = re.compile(r"^rx m=(\d+) cam=([0-9A-F]+) .* pos=" + NUM + "," + NUM + "," + NUM + r"\s*$")
nl_re = re.compile(r"^nl m=(\d+) cam=([0-9A-F]+) on=(\d)(?: k=([0-9.]+))? need=" + NUM + " lift=" + NUM + r"\s*$")

def pct(v, p):
    if not v: return float("nan")
    v = sorted(v); return v[min(len(v) - 1, int(p * len(v)))]

def sgn(x): return (x > 1e-6) - (x < -1e-6)

TOT = {}
BIG = {}
LAG = {}
for path in a.push:
    ticks = []  # [m, Y, need, lift, on, k]
    pend = None
    for ln in open(path, errors="replace"):
        if ln.startswith("nl "):
            mm = nl_re.match(ln)
            pend = (mm.group(2), int(mm.group(3)), float(mm.group(4) or 1), float(mm.group(5)), float(mm.group(6))) if mm else None
        elif ln.startswith("rx ") and pend is not None:
            mm = rx_re.match(ln)
            if mm and mm.group(2) == pend[0] and (a.cam is None or mm.group(2) == a.cam):
                ticks.append([int(mm.group(1)), float(mm.group(4)), pend[3], pend[4], pend[1], pend[2]])
            pend = None
    if a.inject:
        t, u = a.inject.split(":"); t = int(t); u = float(u)
        ticks[t][1] += u
        for j in (t - 1, t, t + 1): ticks[j][2] = max(ticks[j][2], 1e-3)
        print(f"inject: tick {t} m={ticks[t][0]} on={ticks[t][4]} presented Y += {u}")
    segs, cur = [], []
    for q in ticks:
        if cur and q[0] - cur[-1][0] > 960_000: segs.append(cur); cur = []
        cur.append(q)
    if cur: segs.append(cur)
    B = {}
    def bk(key): return B.setdefault(key, dict(wall=[], free=[], alt=[0, 0], altf=[0, 0], ev=[], all=[]))
    for s in segs:
        last_edge = s[0][0]
        for i in range(3, len(s)):
            if (s[i][4], s[i][5]) != (s[i - 1][4], s[i - 1][5]): last_edge = s[i][0]
            w = s[i - 3:i + 1]
            on, k = w[3][4], w[3][5]
            if any((x[4], x[5]) != (on, k) for x in w): continue
            if a.edge > 0 and w[3][0] - last_edge < a.edge * 24e6: continue
            b = bk((on, k))
            Y = [x[1] for x in w]
            d2a = Y[2] - 2 * Y[1] + Y[0]; d2b = Y[3] - 2 * Y[2] + Y[1]
            b["all"].append(abs(d2b))
            if abs(d2b) > 0.5:
                BIG.setdefault((on, k), [0, 0, 0]); g = BIG[(on, k)]
                cls = 0 if any(x[2] > 0 for x in w) else (1 if any(x[3] > 0 for x in w) else 2)
                g[cls] += 1
                if a.lag and cls == 2:
                    ln = next((i - j for j in range(i - 1, -1, -1) if s[j][2] > 0), -1)
                    ll = next((i - j for j in range(i - 1, -1, -1) if s[j][3] > 0), -1)
                    LAG.setdefault((on, k), []).append((ln, ll, round(abs(d2b), 3)))
            if w[3][2] > 0 or w[2][2] > 0:
                b["wall"].append(abs(d2b)); b["ev"].append((abs(d2b), w[3][0], w[3][3]))
                if sgn(d2a) and sgn(d2b): b["alt"][0] += 1; b["alt"][1] += sgn(d2a) != sgn(d2b)
            elif all(x[2] == 0 for x in w):
                b["free"].append(abs(d2b))
                if sgn(d2a) and sgn(d2b): b["altf"][0] += 1; b["altf"][1] += sgn(d2a) != sgn(d2b)
    print(f"== {path}: ticks {len(ticks)} segs {len(segs)}")
    off = [b for (on, k), b in B.items() if on == 0]
    ref = off[0] if off else None
    ref99 = pct(ref["wall"], .99) if ref else float("nan")
    refalt = ref["alt"][1] / ref["alt"][0] if ref and ref["alt"][0] else float("nan")
    for (on, k) in sorted(B):
        b = B[(on, k)]
        al = b["alt"]; r = al[1] / al[0] if al[0] else float("nan")
        hop = sum(1 for x in b["wall"] if x > ref99) if ref else -1
        print(f"  on={on} k={k:g}: wall n {len(b['wall'])} |d2Y| p50 {pct(b['wall'], .5):.4f} p90 {pct(b['wall'], .9):.4f} "
              f"p99 {pct(b['wall'], .99):.4f} max {max(b['wall'], default=0):.4f} | free n {len(b['free'])} p99 {pct(b['free'], .99):.4f} | "
              f"sign-alt wall {al[1]}/{al[0]}={r:.3f} free {b['altf'][1]}/{b['altf'][0]} | over off-wall p99 {hop}")
        n = len(b["all"]) or 1
        print(f"    rate per 1e3 arm ticks (n {len(b['all'])}): |d2Y|>0.25 {1e3 * sum(x > .25 for x in b['all']) / n:.2f}  "
              f">0.5 {1e3 * sum(x > .5 for x in b['all']) / n:.2f}  >1.0 {1e3 * sum(x > 1.0 for x in b['all']) / n:.2f}")
        TOT.setdefault((on, k), [0, 0, 0, 0]); T = TOT[(on, k)]; T[0] += len(b["all"])
        T[1] += sum(x > .25 for x in b["all"]); T[2] += sum(x > .5 for x in b["all"]); T[3] += sum(x > 1.0 for x in b["all"])
        if on == 1 and ref:
            j = pct(b["wall"], .99)
            v = "H-hop" if j > 1.5 * ref99 else ("H-shake" if al[0] >= 30 and r > 1.5 * refalt else "H-smooth")
            print(f"  verdict on k={k:g}: {v} (p99 ratio {j / ref99:.2f}, alt ratio {r / refalt:.2f})")
    if a.top:
        ev = [e for (on, k), b in B.items() if on == 1 for e in b["ev"]]
        seen = []
        for d, m, l in sorted(ev, reverse=True):
            if any(abs(m - x) < 24_000_000 for x in seen): continue
            seen.append(m); print(f"  top on-wall |d2Y| {d:.4f} m={m} lift {l:.4f}")
            if len(seen) >= a.top: break
print("POOLED rate per 1e3 ticks:")
for key in sorted(TOT):
    T = TOT[key]; n = T[0] or 1
    print(f"  on={key[0]} k={key[1]:g}: n {T[0]}  >0.25 {T[1]} ({1e3*T[1]/n:.2f})  >0.5 {T[2]} ({1e3*T[2]/n:.2f})  >1.0 {T[3]} ({1e3*T[3]/n:.2f})")
print("POOLED >0.5 events by window: need>0 / lift>0 only / neither (open flight, not the lift):")
for key in sorted(BIG): print(f"  on={key[0]} k={key[1]:g}: {BIG[key]}")
if a.lag:
    print("s7120 'neither' >0.5 events: (ticks since need>0, ticks since lift>0, |d2Y|); -1 = none in segment")
    for key in sorted(LAG):
        v = LAG[key]; print(f"  on={key[0]} k={key[1]:g}: n {len(v)} sinceNeed<=8 {sum(0 <= x[0] <= 8 for x in v)} sinceLift<=8 {sum(0 <= x[1] <= 8 for x in v)} | {sorted(v)}")
