#!/usr/bin/env python3
"""s7060: one table for the 21:9 dd6 auto-path per-level fps survey (s7058 recipes).

For every level with a TL ring scratch/<dir>/tl_L<L><suf>.bin* and a run log
scratch/agent/m6/g1_lvl<L>s7031L<L><suf>/run.log, runs tools/g5e_cost_by_parity.py
(--phases 1 --skip-s <skip>, with and without --gaps) and prints:
  whole fps, fps excluding >gap-ms stalls, gaps n / per 100 s, rsp mean/p90, P(>=2VI),
  the harness arm line fields (inits, mission_cycles, alive_at_end, crashlines, vi_stalls30s),
  the [s7056] k the level ran with, and the NEXT.md verdict:
    LAGGARD  excl-fps < --fps-bar and (rsp_mean >= --rsp-bar or the >=2-VI frames are RSP-bound,
             mean rsp >= --slow-rsp-bar; s7060 L9: rsp mean 10.5 but slow frames 16.9)  (level K candidate)
    LOWFPS   excl-fps < --fps-bar but rsp is low (not a K lever; look at the gaps)
    OK       otherwise
    CRASH    alive_at_end!=1 or crashlines!=0
usage: tools/s7060_survey_table.py [--dir scratch/s7058] [--suf a] [--levels 0-18]
"""
import argparse, glob, os, re, subprocess, sys

ap = argparse.ArgumentParser()
ap.add_argument('--dir', default='scratch/s7058')
ap.add_argument('--suf', default='a')
ap.add_argument('--levels', default='0-18')
ap.add_argument('--skip', default='130')
ap.add_argument('--gap-ms', default='150')
ap.add_argument('--fps-bar', type=float, default=59.5)
ap.add_argument('--rsp-bar', type=float, default=12.5)
ap.add_argument('--slow-ms', default='25', help='frames longer than this are "slow" (>=2 VI)')
ap.add_argument('--slow-rsp-bar', type=float, default=16.0, help='slow frames whose mean rsp >= this are RSP-bound')
a = ap.parse_args()

def levels(spec):
    out = []
    for part in spec.split(','):
        if '-' in part:
            lo, hi = part.split('-'); out += range(int(lo), int(hi) + 1)
        else:
            out.append(int(part))
    return out

def run(args):
    p = subprocess.run([sys.executable, 'tools/g5e_cost_by_parity.py'] + args, capture_output=True, text=True)
    return p.stdout + p.stderr

hdr = f"{'L':>3} {'fps':>6} {'excl':>6} {'gaps':>5} {'/100s':>6} {'gap_s':>6} {'rsp':>6} {'rsp90':>6} {'P2VI':>5} {'inits':>5} {'cyc':>3} {'alive':>5} {'crash':>5} {'k':>5} {'slow':>5} {'slowrsp':>7}  verdict"
print(hdr)
for L in levels(a.levels):
    tl = sorted(glob.glob(f"{a.dir}/tl_L{L}{a.suf}.bin*"))
    log = f"scratch/agent/m6/g1_lvl{L}s7031L{L}{a.suf}/run.log"
    if not tl or not os.path.exists(log):
        continue
    base = ['--phases', '1', '--skip-s', a.skip]
    g = run(base + ['--gaps', a.gap_ms] + tl + [log])
    w = run(base + tl + [log])
    sl = re.search(r'gaps>\d+ms: n=(\d+) sum=[\d.]+s\s+run=[\d.]+s blk=[\d.]+s rsp=([\d.]+)s', run(base + ['--gaps', a.slow_ms] + tl + [log]))
    slow_n = int(sl.group(1)) if sl else 0
    slow_rsp = 1e3 * float(sl.group(2)) / slow_n if slow_n else 0.0
    m = re.search(r'gaps>\d+ms: n=(\d+) sum=([\d.]+)s', g)
    ex = re.search(r'fps excluding these gaps.*: ([\d.]+)\s*$', g, re.M)
    row = [l for l in w.splitlines() if re.match(r'\s*p0\s', l)]
    if not (m and ex and row):
        print(f"{L:>3} parse failed"); continue
    f = row[-1].split()
    n, fps, rsp, rsp90, p2 = int(f[1]), float(f[2]), float(f[6]), float(f[7]), float(f[-1])
    span = n / fps if fps else 0
    arm = {}
    out = f"{a.dir}/arm_L{L}{a.suf}.out"
    if os.path.exists(out):
        last = open(out, errors='replace').read().strip().splitlines()[-1:]
        arm = dict(kv.split('=', 1) for kv in (last[0].split() if last else []) if '=' in kv)
    k = '?'
    kl = f"{a.dir}/klog_L{L}{a.suf}.txt"
    if os.path.exists(kl):
        km = re.search(rf'level={L} k=([\d.]+)', open(kl, errors='replace').read())
        k = km.group(1) if km else '?'
    gn, gs, exf = int(m.group(1)), float(m.group(2)), float(ex.group(1))
    alive, crash = arm.get('alive_at_end', '?'), arm.get('crashlines', '?')
    if alive != '1' or crash != '0':
        v = 'CRASH'
    elif exf < a.fps_bar and (rsp >= a.rsp_bar or slow_rsp >= a.slow_rsp_bar):
        v = 'LAGGARD'
    elif exf < a.fps_bar:
        v = 'LOWFPS'
    else:
        v = 'OK'
    print(f"{L:>3} {fps:6.2f} {exf:6.2f} {gn:5d} {100*gn/max(span,1e-9):6.1f} {gs:6.2f} {rsp:6.2f} {rsp90:6.2f} {p2:5.2f} "
          f"{arm.get('inits','?'):>5} {arm.get('mission_cycles','?'):>3} {alive:>5} {crash:>5} {k:>5} {slow_n:5d} {slow_rsp:7.2f}  {v}")
