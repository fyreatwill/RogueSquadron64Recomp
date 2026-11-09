#!/usr/bin/env python3
"""s7026 G1c (g1c-gfx-percell): split the DPC submit cost of a ROGUESQ_DD_WIDEWIN=tog3 run by cap phase from the
ROGUESQ_G1E_TRING ring extended by ROGUESQ_S7026_SUB=1 (29 columns).
usage: s7026_submit_split.py RING [--t0-s 0] [--spin-us 1.0]
Per task: dpc = submit(sampled x16) + commit; rt = time inside ultramodern::submit_rdp_range (RT64 handoff, exact);
rec = rs64_dpc_record_submit (exact); self = dpc - rt - rec (bridge self). wait = 1 - cpu/wall of the 1/16-sampled RT64 calls.
Control: spin_win=1 rows (SPIN_NS after every RT64 handoff) must show rt/call up by ~spin and sd_wall up by ~rt_n*spin.
Discriminator: per-task least squares rt ~ a*rt_n + b*rt_bytes + c (pooled and within each cap): the share of the cap delta
carried by a*d(rt_n) (H-percall) vs b*d(bytes) (H-perbyte); wait share (H-sync)."""
import sys, argparse
import statistics
ap = argparse.ArgumentParser(); ap.add_argument('ring'); ap.add_argument('--t0-s', type=float, default=0.0)
ap.add_argument('--spin-us', type=float, default=300.0)
a = ap.parse_args()
R = []
for l in open(a.ring):
    if l.startswith('#'): continue
    f = l.split()
    if len(f) < 29: continue
    t, w, c, uc, sub, com = map(float, f[:6]); calls, by, n, ph, sp = map(int, f[6:11]); rng = int(f[12])
    cap0, cap1, capx, rt_n = int(f[17]), int(f[18]), int(f[19]), int(f[20]); rt_us = float(f[21]); rt_by = int(f[22])
    rec_n = int(f[23]); rec_us = float(f[24]); smp_n = int(f[25]); smp_w = float(f[26]); smp_c = float(f[27]); sw = int(f[28])
    R.append(dict(t=t, w=w, c=c, gap=w - c, uc=uc, dpc=sub + com, sub=sub, com=com, calls=calls, by=by, n=n, ph=ph, rng=rng,
                  cap=cap0, capx=capx or cap0 != cap1, rt_n=rt_n, rt=rt_us / 1e3, rt_by=rt_by, rec_n=rec_n, rec=rec_us / 1e3,
                  self=sub + com - rt_us / 1e3 - rec_us / 1e3, smp_n=smp_n, smp_w=smp_w, smp_c=smp_c, sw=sw))
print(f"rows={len(R)}")
if not R: sys.exit(1)
# time per row = interval since previous row (for fps per cap)
for i, r in enumerate(R): r['dt'] = (r['t'] - R[i - 1]['t']) if i else 0.0
tmin = R[0]['t'] + a.t0_s * 1000
ph = {}
for r in R:
    if r['t'] >= tmin and r['cap'] > 0: ph[r['ph']] = ph.get(r['ph'], 0) + 1
fph = max(ph, key=ph.get)
F = [r for r in R if r['t'] >= tmin and r['ph'] == fph and r['n'] == 1 and not r['capx'] and r['cap'] > 0 and r['dt'] < 200]
print(f"flight phase={fph} rows_used={len(F)} (dropped cap-mixed/multi-ucode/gap>200ms)")
K = ['w', 'c', 'gap', 'uc', 'sub', 'com', 'dpc', 'rt', 'rec', 'self', 'calls', 'rng', 'rt_n', 'by', 'rt_by']
m = lambda g, k: sum(r[k] for r in g) / len(g) if g else float('nan')
caps = sorted({r['cap'] for r in F})
G = {}
for sw in (0, 1):
    for cp in caps:
        G[(sw, cp)] = [r for r in F if r['sw'] == sw and r['cap'] == cp]
print("\nper task means (ms; counts; bytes)  fps = tasks / summed row intervals")
print("sw cap   tasks  fps   " + " ".join(f"{k:>9}" for k in K) + "   ns/rt_call ns/rt_byte  wait%")
for (sw, cp), g in G.items():
    if not g: continue
    fps = len(g) / (sum(r['dt'] for r in g) / 1000.0)
    sw_ = sum(r['smp_w'] for r in g); sc_ = sum(r['smp_c'] for r in g)
    rtn = sum(r['rt_n'] for r in g); rtb = sum(r['rt_by'] for r in g); rtt = sum(r['rt'] for r in g) * 1e6
    print(f"{sw}  {cp:5d} {len(g):6d} {fps:5.1f} " + " ".join(f"{m(g, k):9.3f}" if k not in ('calls', 'rng', 'rt_n', 'by', 'rt_by') else f"{m(g, k):9.0f}" for k in K)
          + f"   {rtt / max(rtn, 1):9.1f} {rtt / max(rtb, 1):9.3f}  {100 * (1 - sc_ / max(sw_, 1e-9)):5.1f}")
# spin control
print("\ncontrol (spin windows): rt/call rise must be ~%.2f us; sd_wall rise ~ rt_n*spin" % a.spin_us)
for cp in caps:
    g0, g1 = G[(0, cp)], G[(1, cp)]
    if not g0 or not g1: continue
    pc0 = sum(r['rt'] for r in g0) / sum(r['rt_n'] for r in g0) * 1e3; pc1 = sum(r['rt'] for r in g1) / sum(r['rt_n'] for r in g1) * 1e3
    print(f"  cap {cp}: rt/call {pc0:.3f} -> {pc1:.3f} us (d {pc1 - pc0:+.3f}); sd_wall d {m(g1, 'w') - m(g0, 'w'):+.3f} ms vs predicted "
          f"{m(g1, 'rt_n') * a.spin_us / 1e3:+.3f}; rt d {m(g1, 'rt') - m(g0, 'rt'):+.3f}")
# deltas between caps (no-spin)
if len(caps) >= 2:
    lo, hi = G[(0, caps[0])], G[(0, caps[-1])]
    print(f"\ncap delta {caps[-1]} - {caps[0]} (no-spin):")
    for k in K: print(f"  {k:6s} {m(hi, k) - m(lo, k):+10.3f}   ({m(lo, k):.3f} -> {m(hi, k):.3f})")
    # A/A: split the high cap rows by alternating 1-s blocks of t
    A = [r for r in hi if int(r['t'] // 1000) % 2 == 0]; B = [r for r in hi if int(r['t'] // 1000) % 2 == 1]
    print("  A/A (cap %d, even vs odd seconds): " % caps[-1] + " ".join(f"{k} {m(A, k) - m(B, k):+.3f}" for k in ('w', 'dpc', 'rt', 'rec', 'self', 'rt_n')))
def fit(rows, y, xs):
    """ordinary least squares via normal equations (pure python, few regressors); returns (coefs + [intercept], R2)."""
    X = [[r[x] for x in xs] + [1.0] for r in rows]; Y = [r[y] for r in rows]; p = len(xs) + 1
    # centre-free normal equations, scaled per column for conditioning
    sc = [max(abs(v[j]) for v in X) or 1.0 for j in range(p)]
    Xs = [[v[j] / sc[j] for j in range(p)] for v in X]
    A = [[sum(v[i] * v[j] for v in Xs) for j in range(p)] + [sum(v[i] * yy for v, yy in zip(Xs, Y))] for i in range(p)]
    for i in range(p):
        piv = max(range(i, p), key=lambda k: abs(A[k][i])); A[i], A[piv] = A[piv], A[i]
        if abs(A[i][i]) < 1e-12: return [float('nan')] * p, float('nan')
        for k in range(p):
            if k != i:
                fct = A[k][i] / A[i][i]
                A[k] = [a_ - fct * b_ for a_, b_ in zip(A[k], A[i])]
    co = [A[i][p] / A[i][i] / sc[i] for i in range(p)]
    pred = [sum(c_ * v_ for c_, v_ in zip(co, v)) for v in X]
    my = sum(Y) / len(Y); sst = sum((yy - my) ** 2 for yy in Y); sse = sum((yy - pp) ** 2 for yy, pp in zip(Y, pred))
    return co, (1 - sse / sst) if sst > 0 else float('nan')
print("\nleast squares per task (no-spin rows), coefficient units: ms per unit")
for y, xs in (('rt', ['rt_n', 'rt_by']), ('self', ['calls', 'by']), ('rec', ['rec_n', 'rt_by']), ('dpc', ['calls', 'rt_n', 'by'])):
    rows = [r for r in F if r['sw'] == 0]
    co, r2 = fit(rows, y, xs)
    s = f"  {y:5s} pooled: " + " ".join(f"{x}={co[i] * 1e6:.2f}ns" for i, x in enumerate(xs)) + f" c={co[-1]:.3f}ms R2={r2:.3f}"
    if len(caps) >= 2:
        lo, hi = G[(0, caps[0])], G[(0, caps[-1])]
        parts = [co[i] * (m(hi, x) - m(lo, x)) for i, x in enumerate(xs)]
        s += " | cap delta explained: " + " ".join(f"{x} {p:+.3f}" for x, p in zip(xs, parts)) + f" (obs {m(hi, y) - m(lo, y):+.3f})"
    print(s)
    for cp in caps:
        g = G[(0, cp)]
        if len(g) > 50:
            co2, r22 = fit(g, y, xs)
            print(f"        within cap {cp}: " + " ".join(f"{x}={co2[i] * 1e6:.2f}ns" for i, x in enumerate(xs)) + f" c={co2[-1]:.3f} R2={r22:.3f}")
