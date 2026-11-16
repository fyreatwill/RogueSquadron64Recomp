#!/usr/bin/env python3
"""s7432 class CO: same-run 2x2 A/B (quiet x busy) from a timestamped run.tlog (tools/s7431_stderr_volume.sh with
ROGUESQ_G1E_AQ=2 ROGUESQ_DIAG_QUIET_TOGGLE=<a> ROGUESQ_DIAG_BUSY_TOGGLE=<2a> ROGUESQ_DIAG_BUSY_US / _BUSY_GUEST_US).
Per state: [g1e-split] mean ucode_ms per gfx task and tasks/s (the row right after a flip is dropped), plus the direct
cost from [diag-quiet] win lines (fprintf ms per wall second on gfx-task vs other threads).
CONTROL: busy=1 must raise ucode_ms by >= 0.5*BUSY_US. Exit 0 = control pass, 3 = control fail.
usage: s7432_diag_quiet_ab.py run.tlog [--from 80] [--busy-us 1000]"""
import re, sys, argparse, statistics as st
ap = argparse.ArgumentParser(); ap.add_argument("tlog"); ap.add_argument("--from", dest="t0", type=float, default=80.0)
ap.add_argument("--busy-us", type=float, default=1000.0); a = ap.parse_args()
row = re.compile(r"\[g1e-split\] phase=\d+ .*?tasks=(\d+) ucode_ms=([\d.]+)")
flip = re.compile(r"\[diag-quiet\] flip quiet=(\d) busy=(\d)")
win = re.compile(r"\[diag-quiet\] win quiet=(\d) busy=(\d) t=[\d.]+ secs=([\d.]+) task_calls=(\d+) task_ms=([\d.]+) task_bytes=(\d+) "
                 r"task_drop=(\d+) oth_calls=(\d+) oth_ms=([\d.]+) oth_bytes=(\d+) oth_drop=(\d+)")
state = (0, 0); skip = False; rows = {}; wins = {}
for raw in open(a.tlog, "rb"):
    l = raw.decode("utf-8", "replace"); ms, _, l = l.partition("\t"); t = int(ms) / 1000.0
    m = win.search(l)
    if m and t >= a.t0:
        k = (int(m[1]), int(m[2])); w = wins.setdefault(k, [0.0] * 9)
        for i, v in enumerate((m[3], m[4], m[5], m[6], m[7], m[8], m[9], m[10], m[11])): w[i] += float(v)
    m = flip.search(l)
    if m: state = (int(m[1]), int(m[2])); skip = True; continue
    m = row.search(l)
    if not m: continue
    if skip: skip = False; continue
    if t < a.t0 or int(m[1]) == 0: continue
    rows.setdefault(state, []).append((int(m[1]), float(m[2])))
print("state(q,b) | rows | ucode_ms mean+-se | tasks/s mean+-se | fprintf task-thr ms/s calls/s KB/s drop/s | other-thr ms/s calls/s KB/s drop/s")
res = {}
for k in sorted(set(rows) | set(wins)):
    r = rows.get(k, []); w = wins.get(k)
    if len(r) >= 3:
        u = [x[1] for x in r]; n = [x[0] for x in r]
        se = lambda v: st.stdev(v) / len(v) ** 0.5
        res[k] = (st.mean(u), st.mean(n)); s = f"{len(r):4d} | {st.mean(u):.3f}+-{se(u):.3f} | {st.mean(n):.1f}+-{se(n):.1f}"
    else: s = f"{len(r):4d} | (too few rows)"
    if w and w[0] > 0:
        d = w[0]; s += (f" | {w[2]/d:.3f} {w[1]/d:.0f} {w[3]/d/1024:.1f} {w[4]/d:.0f} | {w[6]/d:.3f} {w[5]/d:.0f} {w[7]/d/1024:.1f} {w[8]/d:.0f}"
                        f"  ({d:.0f} s)")
    print(f"{k} | {s}")
ok = all(k in res for k in [(0, 0), (0, 1), (1, 0), (1, 1)])
if not ok: print("CONTROL FAIL: missing states"); sys.exit(3)
db = ((res[(0, 1)][0] - res[(0, 0)][0]) + (res[(1, 1)][0] - res[(1, 0)][0])) / 2
dq = ((res[(1, 0)][0] - res[(0, 0)][0]) + (res[(1, 1)][0] - res[(0, 1)][0])) / 2
fb = ((res[(0, 1)][1] - res[(0, 0)][1]) + (res[(1, 1)][1] - res[(1, 0)][1])) / 2
fq = ((res[(1, 0)][1] - res[(0, 0)][1]) + (res[(1, 1)][1] - res[(0, 1)][1])) / 2
print(f"effect busy: ucode {db:+.3f} ms/task, tasks/s {fb:+.1f} | effect quiet: ucode {dq:+.3f} ms/task, tasks/s {fq:+.1f}")
if db < 0.5 * a.busy_us / 1000: print("CONTROL FAIL: busy control did not move ucode_ms"); sys.exit(3)
print("CONTROL PASS")
