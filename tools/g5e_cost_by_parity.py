#!/usr/bin/env python3
"""s7010 G5e: split per-frame cost of a ROGUESQ_DD_WIDEWIN=tog run by toggle parity.

Inputs: the s6711 G1E_TL ring (<file>.<pid>, marks <qIIii: t_us steady_clock, code, arg, osid, slot>) and the run's
stderr/run.log carrying the s7010 anchor '[s7010-clk] steady_us=S mach=M'. Tog parity = (mach_absolute_time / 24e6) & 1,
mach = M + (t_us - S) * 24 (24 MHz timebase; anchor is taken in the same process, so sleep offsets cancel).
Per game frame (osViSwapBuffer by the game thread to the next): T, run (game thread not blocked = guest CPU incl. terrain
stream/mesh build), rsp (gfx task start -> RSP ucode exit, i.e. LLE F5 ucode host time), rdp (RSP exit -> send_dl return,
RT64 submit), dpc (send_dl return -> dp_complete), VIs crossed. Frames within --guard-ms of a parity flip are dropped.
Positive control: T(on) > T(off) must reproduce the s7009 captured-fps drop (~60 -> ~50); a parity mapping error would
average both arms together and show no difference. Sanity: run the same split with parity shifted 0.5 s (--shift-ms 500)
and the deltas must collapse toward 0.
Usage: g5e_cost_by_parity.py <tl.bin.pid> <log-with-anchor> [--skip-s 130] [--guard-ms 60]
"""
import struct, sys, argparse, re, bisect, statistics as st
ap = argparse.ArgumentParser(); ap.add_argument('tl'); ap.add_argument('log')
ap.add_argument('--skip-s', type=float, default=130.0); ap.add_argument('--guard-ms', type=float, default=60.0); ap.add_argument('--shift-ms', type=float, default=0.0)
ap.add_argument('--until-s', type=float, default=1e9, help='s7021: drop marks later than this many s after the ring start (match an xctrace window)')
ap.add_argument('--phases', type=int, default=2, help='s7012: 3 = WIDEWIN=tog3, phase=(mach/24e6)%%3 -> cap a/b/c')
ap.add_argument('--split', choices=('parity', 'xor8', 'hash'), default=None,
                help='s7017: arm of a mach second s. parity = s&1 (s7010, biased by the autopilot 2 s press cycle); xor8 = (s ^ s>>3)&1 '
                     '(rs64_tog_odd: cancels any 8 s-periodic load exactly over 16 s); hash = splitmix32(s)&1 (unbiased, ~6x noisier)')
ap.add_argument('--gaps', type=float, default=0.0, help='s7059: also list every frame with T > this many ms (t since ring start, run/blk/rsp split)')
ap.add_argument('--inject-ms', type=float, default=0.0, help='s7017 estimator control: add this to rsp of on-arm frames')
a = ap.parse_args()
m = None
for ln in open(a.log, errors='replace'):
    mm = re.search(r'\[s7010-clk\] steady_us=(-?\d+) mach=(\d+)(?: split=(\w+))?', ln)
    if mm: m = (int(mm.group(1)), int(mm.group(2))); split_log = mm.group(3) or 'parity'; break
if not m and a.phases == 1:  # s7059: auto-path (no tog) runs print no anchor; one phase needs none and has no flips to guard
    m = (0, 0); split_log = 'parity'; a.guard_ms = 0.0; print('no anchor: --phases 1, whole run is one arm, guard off')
if not m: sys.exit('no [s7010-clk] anchor in log')
S, M = m
if a.split is None: a.split = split_log  # s7017: the anchor names the split the run toggled on (absent = s7010 parity)
print(f'split={a.split} (anchor: {split_log})')
M += int(a.shift_ms * 24000)
raw = open(a.tl, 'rb').read(); n = len(raw) // 24
ev = sorted((r[0], r[1], r[2], r[4]) for r in (struct.unpack_from('<qIIii', raw, i * 24) for i in range(n)) if r[0] != 0)
t0 = ev[0][0]; ev = [e for e in ev if a.skip_s * 1e6 <= e[0] - t0 < a.until_s * 1e6]
import collections
G = collections.Counter(e[3] for e in ev if e[1] == 15).most_common(1)[0][0]
vis = [e[0] for e in ev if e[1] == 1]
def h32(x):
    x = (x + 0x9E3779B9) & 0xFFFFFFFF; x ^= x >> 16; x = (x * 0x85EBCA6B) & 0xFFFFFFFF
    x ^= x >> 13; x = (x * 0xC2B2AE35) & 0xFFFFFFFF; x ^= x >> 16; return x
def par(t):
    sec = int((M + (t - S) * 24) // 24000000)
    if a.phases == 2 and a.split == 'xor8': return (sec ^ (sec >> 3)) & 1
    if a.phases == 2 and a.split == 'hash': return h32(sec & 0xFFFFFFFF) & 1
    return sec % a.phases
def flip_dist_ms(t):
    x = (M + (t - S) * 24) % 24000000; return min(x, 24000000 - x) / 24000.0
sw = [i for i, e in enumerate(ev) if e[1] == 15 and e[3] == G]
fr = []
for k in range(len(sw) - 1):
    a0, a1 = sw[k], sw[k + 1]; ta, tb = ev[a0][0], ev[a1][0]
    blk = 0.0; op = None; last6 = None; rsp = rdp = dpc = 0.0; ex7 = None; ex8 = None
    for x in range(a0, a1):
        e = ev[x]
        if e[3] == G:
            if e[1] == 10: op = e[0]
            elif e[1] == 11 and op is not None: blk += (e[0] - op) / 1e3; op = None
        if e[1] == 6: last6 = e[0]
        elif e[1] == 7 and last6 is not None: rsp += (e[0] - last6) / 1e3; ex7 = e[0]; last6 = None
        elif e[1] == 8 and ex7 is not None: rdp += (e[0] - ex7) / 1e3; ex8 = e[0]; ex7 = None
        elif e[1] == 9 and ex8 is not None: dpc += (e[0] - ex8) / 1e3; ex8 = None
    if op is not None: blk += (tb - op) / 1e3
    pa, pb = par(ta), par(tb)
    if pa != pb or flip_dist_ms(ta) < a.guard_ms or flip_dist_ms(tb) < a.guard_ms: continue
    nvi = bisect.bisect_right(vis, tb) - bisect.bisect_right(vis, ta)
    if pa == 1: rsp += a.inject_ms
    fr.append(dict(p=pa, T=(tb - ta) / 1e3, run=(tb - ta) / 1e3 - blk, rsp=rsp, rdp=rdp, dpc=dpc, nvi=nvi, t=(ta - t0) / 1e6, blk=blk))
if a.gaps > 0:
    gl = [f for f in fr if f['T'] > a.gaps]
    print(f"gaps>{a.gaps:.0f}ms: n={len(gl)} sum={sum(f['T'] for f in gl)/1e3:.2f}s  run={sum(f['run'] for f in gl)/1e3:.2f}s blk={sum(f['blk'] for f in gl)/1e3:.2f}s rsp={sum(f['rsp'] for f in gl)/1e3:.2f}s")
    span = sum(f['T'] for f in fr) / 1e3; gs = sum(f['T'] for f in gl) / 1e3
    print(f"fps excluding these gaps (s7059: menu/cutscene/mission-end transitions on harness mission cycles): {(len(fr) - len(gl)) / max(1e-9, span - gs):.2f}")
    for f in gl: print(f"  t={f['t']:7.1f}s T={f['T']:6.1f} run={f['run']:6.1f} blk={f['blk']:6.1f} rsp={f['rsp']:6.1f} rdp={f['rdp']:5.1f} vi={f['nvi']}")
def pct(v, q): v = sorted(v); return v[min(len(v) - 1, int(q * len(v)))]
print(f'marks={n} game slot={G} frames kept={len(fr)} (guard {a.guard_ms} ms, skip {a.skip_s} s)')
print(' arm  n     fps    T_mean  run_mean run_p90  rsp_mean rsp_p90  rdp_mean dpc_mean  P(>=2VI)')
res = {}
for p, nm in (((0, 'off'), (1, 'on')) if a.phases == 2 else tuple((i, 'p%d' % i) for i in range(a.phases))):
    r = [f for f in fr if f['p'] == p]
    if not r: continue
    res[nm] = {k: st.mean(f[k] for f in r) for k in ('T', 'run', 'rsp', 'rdp', 'dpc')}
    print(f' {nm:3s} {len(r):5d} {1000 / res[nm]["T"]:6.1f} {res[nm]["T"]:7.2f} {res[nm]["run"]:8.2f} {pct([f["run"] for f in r], .9):7.2f} '
          f'{res[nm]["rsp"]:8.2f} {pct([f["rsp"] for f in r], .9):7.2f} {res[nm]["rdp"]:8.2f} {res[nm]["dpc"]:8.2f} '
          f'{sum(f["nvi"] >= 2 for f in r) / len(r):8.2f}')
if 'on' in res and 'off' in res:
    print(' delta on-off (ms/frame): ' + ', '.join(f'{k} {res["on"][k] - res["off"][k]:+.2f}' for k in ('T', 'run', 'rsp', 'rdp', 'dpc')))
if a.phases > 2 and 'p0' in res:
    for i in range(1, a.phases):
        if 'p%d' % i in res: print(' delta p%d-p0 (ms/frame): ' % i + ', '.join(f'{k} {res["p%d" % i][k] - res["p0"][k]:+.2f}' for k in ('T', 'run', 'rsp', 'rdp', 'dpc')))
