#!/usr/bin/env python3
"""s7766 input-to-photon latency. Joins three logs of ONE run on the mach_absolute_time clock:
  [inlat] m=<ticks> btn sx sy   every guest pad read (ROGUESQ_S7766_INLAT=1, src/main/main.cpp get_n64_input)
  [g3c] vi= m=<ticks> cam=16f pl=12f   guest state sampled at each VI (ROGUESQ_G3C_LOG=1, events.cpp)
  ring Q/P rows                       present queue time / CoreAnimation presentedTime (ROGUESQ_PRESENT_RING)
For each autopilot stick step (sx 0 -> +-k) it finds the first poll carrying the step (t_in), the first VI whose sampled
state departs from the pre-step trend (t_state; per channel group cam / pl, earliest wins), and the first present queued
after that VI that reached the screen (t_photon). Prints per-arm medians of poll->state, state->photon, poll->photon,
game frames (distinct state samples) between poll and response, and the poll rate.
Control (--ctl): the same detector run at fake step times 0.9 s after each real step's RELEASE window midpoint where the
stick is constant must find no response within the window far more often than the real steps (detector specificity).
usage: s7766_inlat.py <log> <ring> [--ctl] [--win 0.25]"""
import re, sys, math, statistics as st, argparse
ap = argparse.ArgumentParser(); ap.add_argument('log'); ap.add_argument('ring'); ap.add_argument('--ctl', action='store_true')
ap.add_argument('--win', type=float, default=0.25); ap.add_argument('--k', type=float, default=6.0); ap.add_argument('--floor', type=float, default=0.15); a = ap.parse_args()
TICK = 125 / 3 * 1e-9  # Apple Silicon mach timebase (ring t = ticks * TICK, checked below)
polls = []; vis = []; DLS = []
for l in open(a.log, errors='replace'):
    if l.startswith('[inlat-dl] '):
        m = re.match(r'\[inlat-dl\] m=(\d+) n=(\d+) dl=\w+ c0=(\S+) c2=(\S+)', l)
        if m: DLS.append((int(m[1]) * TICK, int(m[2]), math.degrees(math.atan2(float(m[4]), float(m[3])))))
        continue
    if l.startswith('[inlat] '):
        m = re.match(r'\[inlat\] m=(\d+) btn=(\w+) sx=(-?\d+) sy=(-?\d+)', l)
        if m: polls.append((int(m[1]) * TICK, int(m[2], 16), int(m[3]), int(m[4])))
    elif l.startswith('[g3c] '):
        m = re.search(r' m=(\d+) .*cam=(\S+) pl=(\S+)', l)
        if not m: continue
        try: cam = [float(x) for x in m[2].split(',')]; pl = [float(x) for x in m[3].rstrip(',').split(',')]
        except ValueError: continue
        if len(cam) == 16 and len(pl) == 12: vis.append((int(m[1]) * TICK, cam, pl))
Q = []; P = {}; WLQ = {}  # wl id (= gfx task ordinal + 1, s7766 7493/7543 + 4274/4274 presents) -> first Q
for l in open(a.ring, errors='replace'):
    if l[:2] == 'Q ':
        p = l.split()
        if len(p) > 4 and 'skip=0' in p:
            Q.append((float(p[1]), int(re.search(r'mtl=(\d+)', l)[1])))
            w = re.search(r' wl=(\d+)', l)
            if w: WLQ.setdefault(int(w[1]), (float(p[1]), Q[-1][1]))
    elif l[:2] == 'P ':
        m = re.match(r'P \S+ mtl=(\d+) at=(\S+)', l)
        if m and float(m[2]) > 0: P[int(m[1])] = float(m[2])
if not polls or not vis or not Q: sys.exit(f'missing rows polls={len(polls)} vis={len(vis)} Q={len(Q)}')
if abs(Q[0][0] - vis[0][0]) > 30: sys.exit(f'clock mismatch ring {Q[0][0]} vs g3c {vis[0][0]}')
dur = polls[-1][0] - polls[0][0]
# Steps: sx 0 -> nonzero, with >= 0.15 s of zero stick before it.
steps = []; zero_since = None
for i, (t, b, sx, sy) in enumerate(polls):
    if sx == 0:
        if zero_since is None: zero_since = t
    else:
        if zero_since is not None and t - zero_since >= 0.15: steps.append((t, sx, zero_since))
        zero_since = None
# Distinct state samples (a VI where cam or pl changed from the previous VI = one new game frame observed).
D = [vis[0]]
for v in vis[1:]:
    if v[1] != D[-1][1] or v[2] != D[-1][2]: D.append(v)
ROT = [0, 1, 2, 4, 5, 6, 8, 9, 10]
def series(sel, lo, hi):
    return [(t, [sel(c, p)[j] for j in range(len(sel(c, p)))]) for t, c, p in D if lo <= t <= hi]
# Heading = atan2(cam[2], cam[0]) (s7766: drifts ~0.01 deg/frame in straight flight, 0.5-1.5 deg/frame within 2 frames of a
# full stick step). The s7766 first draft used every rotation/player float and failed its control (72-89% false hits).
GROUPS = {'heading': lambda c, p: [math.degrees(math.atan2(c[2], c[0]))]}
def detect(t_in, t_pre0):
    """Earliest distinct sample after t_in whose per-frame delta departs from the pre-step deltas by > k sigma."""
    best = None
    for g, sel in GROUPS.items():
        S = series(sel, max(t_pre0, t_in - 0.6), t_in + a.win)
        pre = [(S[i][0], [S[i][1][j] - S[i - 1][1][j] for j in range(len(S[i][1]))]) for i in range(1, len(S)) if S[i][0] <= t_in]
        post = [(S[i][0], [S[i][1][j] - S[i - 1][1][j] for j in range(len(S[i][1]))]) for i in range(1, len(S)) if S[i][0] > t_in]
        if len(pre) < 4 or not post: continue
        n = len(pre[0][1]); hit = None
        mu = [st.mean(d[j] for _, d in pre[-6:]) for j in range(n)]
        sd = [st.pstdev([d[j] for _, d in pre[-6:]]) for j in range(n)]
        for t, d in post:
            dev = [((d[j] - mu[j] + 180) % 360) - 180 for j in range(n)]
            if any(abs(dev[j]) > max(a.floor, a.k * sd[j]) for j in range(n)): hit = t; break
        if hit is not None and (best is None or hit < best[0]): best = (hit, g)
    return best
QP = {}  # Q time of the present that carried each photon
def photon(t_state):
    for t, k in Q:
        if t > t_state and k in P: QP[P[k]] = t; return P[k]
    return None
def run(times):
    rows = []
    for t_in, t0 in times:
        r = detect(t_in, t0)
        if r is None: rows.append(None); continue
        t_state, g = r; ph = photon(t_state)
        frames = sum(1 for t, _, _ in D if t_in < t <= t_state)
        rows.append((t_state - t_in, (ph - t_state) if ph else None, (ph - t_in) if ph else None, frames, g,
                     (QP[ph] - t_state) if ph else None, (ph - QP[ph]) if ph else None))
    return rows
def summ(tag, rows):
    ok = [r for r in rows if r]; ph = [r for r in ok if r[2] is not None]
    if not ok: print(f'{tag}: steps={len(rows)} detected=0'); return
    md = lambda v: st.median(v) * 1e3
    gs = {}; [gs.__setitem__(r[4], gs.get(r[4], 0) + 1) for r in ok]
    fr = {}; [fr.__setitem__(r[3], fr.get(r[3], 0) + 1) for r in ok]
    print(f'{tag}: steps={len(rows)} detected={len(ok)} poll->state p50 {md([r[0] for r in ok]):.1f} ms '
          f'(p10 {sorted(r[0] for r in ok)[len(ok)//10]*1e3:.1f} p90 {sorted(r[0] for r in ok)[9*len(ok)//10]*1e3:.1f}) '
          f'state->photon p50 {md([r[1] for r in ph]):.1f} ms  poll->photon p50 {md([r[2] for r in ph]):.1f} ms '
          f'(p90 {sorted(r[2] for r in ph)[9*len(ph)//10]*1e3:.1f}) [state->queue {md([r[5] for r in ph]):.1f} + queue->photon {md([r[6] for r in ph]):.1f}]  frames-until-response {dict(sorted(fr.items()))} groups {gs}')
print(f'{a.log}: polls={len(polls)} ({len(polls)/dur:.1f}/s) VIs={len(vis)} distinct-state samples={len(D)} ({len(D)/((D[-1][0]-D[0][0]) or 1):.1f}/s) steps={len(steps)}')
real = run([(t, z) for t, _, z in steps])
summ('REAL', real)
if a.ctl:
    # Fake steps inside long constant-stick-zero stretches: 0.30 s after a zero run starts (pre window wholly zero stick), only
    # where the zero run lasts >= 0.30 + win s, so nothing changes in the input over the whole detection window.
    fakes = []; zs = None
    for t, b, sx, sy in polls:
        if sx == 0 and zs is None: zs = t
        if sx != 0 and zs is not None:
            if t - zs >= 0.9 + a.win + 0.05: fakes.append((zs + 0.9, zs + 0.3))
            zs = None
    ctl = run(fakes); fd = sum(1 for r in ctl if r)
    print(f'CTL : fake steps={len(ctl)} false detections={fd} ({100*fd/max(len(ctl),1):.0f}%) vs real {100*sum(1 for r in real if r)/max(len(real),1):.0f}%')

# Exact path (s7766 r2): [inlat-dl] tags each gfx task with the heading it was submitted with; present ring wl = n + 1.
def detect_dl(t_in, t_pre0):
    S = [(t, n, h) for t, n, h in DLS if max(t_pre0, t_in - 0.6) <= t <= t_in + a.win]
    pre = [(S[i][0], ((S[i][2] - S[i-1][2] + 180) % 360) - 180) for i in range(1, len(S)) if S[i][0] <= t_in]
    post = [(S[i][0], S[i][1], ((S[i][2] - S[i-1][2] + 180) % 360) - 180) for i in range(1, len(S)) if S[i][0] > t_in]
    if len(pre) < 4 or not post: return None
    mu = st.mean(d for _, d in pre[-6:]); sd = st.pstdev([d for _, d in pre[-6:]])
    for t, n, d in post:
        if abs(d - mu) > max(a.floor, a.k * sd): return t, n
    return None
def run_dl(times):
    rows = []
    for t_in, t0 in times:
        r = detect_dl(t_in, t0)
        if r is None: rows.append(None); continue
        t_sub, n = r; q = WLQ.get(n + 1); ph = P.get(q[1]) if q else None
        tasks = sum(1 for t, _, _ in DLS if t_in < t <= t_sub)
        rows.append((t_sub - t_in, (q[0] - t_sub) if q else None, (ph - q[0]) if ph else None, (ph - t_in) if ph else None, tasks))
    return rows
def summ_dl(tag, rows):
    ok = [r for r in rows if r]; ph = [r for r in ok if r[3] is not None]
    if not ph: print(f'{tag}: steps={len(rows)} detected={len(ok)} with photon=0'); return
    md = lambda i, v=ph: st.median(x[i] for x in v) * 1e3
    pc = lambda i, q: sorted(x[i] for x in ph)[int(q * (len(ph) - 1))] * 1e3
    tk = {}; [tk.__setitem__(r[4], tk.get(r[4], 0) + 1) for r in ok]
    print(f'{tag}: steps={len(rows)} detected={len(ok)} photon={len(ph)}  poll->submit p50 {md(0):.1f}  submit->queue {md(1):.1f}  '
          f'queue->photon {md(2):.1f}  POLL->PHOTON p50 {md(3):.1f} ms (p10 {pc(3,.1):.1f} p90 {pc(3,.9):.1f})  tasks-until-response {dict(sorted(tk.items()))}')
if DLS:
    real_dl = run_dl([(t, z) for t, _, z in steps]); summ_dl('EXACT', real_dl)
    if a.ctl:
        cd = run_dl(fakes); print(f'CTL-EXACT: fake steps={len(cd)} false detections={sum(1 for r in cd if r)} vs real {sum(1 for r in real_dl if r)}/{len(real_dl)}')
