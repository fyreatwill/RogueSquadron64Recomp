#!/usr/bin/env python3
"""s7590 HR-2 scorer for tools/s7590_portcensus.dylib output.

usage: s7590_pc_report.py census.log --windows a-b,c-d,... [--top N]
Per window (census tick times, seconds since process start) takes the median count of every key, then prints the step
between consecutive windows for every key that moves, plus the right-type totals (R/S/O/P/D). Control: the plant keys
(R/-1/s7590-plant and S/23/unattr) must step by the number of PLANT lines between the windows; rc 1 if they do not.
"""
import re, sys, statistics as st, argparse

ap = argparse.ArgumentParser(); ap.add_argument('log'); ap.add_argument('--windows', required=True); ap.add_argument('--top', type=int, default=40)
a = ap.parse_args()
wins = [tuple(float(x) for x in w.split('-')) for w in a.windows.split(',')]
ticks = []  # (t, totals dict, counts dict)
plants = []
cur = {}
for ln in open(a.log, errors='replace'):
    if ln.startswith('C '):
        m = dict(re.findall(r'(\w+)=(\S+)', ln))
        if 'total' not in m: continue
        cur = dict(cur)
        ticks.append([float(m['t']), {k: int(m[k]) for k in ('total', 'R', 'S', 'O', 'P', 'D')}, cur])
    elif ln.startswith('K '):
        m = re.match(r'K (.*) n=(\d+) d=', ln)
        if m and ticks: ticks[-1][2][m.group(1)] = int(m.group(2))
    elif ln.startswith('PLANT'):
        plants.append(float(re.search(r't=(\d+)', ln).group(1)))
def med(vals): return st.median(vals) if vals else None
rows = []
for lo, hi in wins:
    sel = [t for t in ticks if lo <= t[0] <= hi]
    tot = {k: med([t[1][k] for t in sel]) for k in ('total', 'R', 'S', 'O', 'P', 'D')}
    keys = set().union(*[t[2].keys() for t in sel]) if sel else set()
    rows.append((lo, hi, len(sel), tot, {k: med([t[2].get(k, 0) for t in sel]) for k in keys}))
print('windows:', ' | '.join(f'{lo:.0f}-{hi:.0f} n={n} total={t["total"]} R={t["R"]} S={t["S"]} O={t["O"]} P={t["P"]} D={t["D"]}' for lo, hi, n, t, _ in rows))
allk = set().union(*[r[4].keys() for r in rows])
moving = []
for k in allk:
    v = [r[4].get(k, 0) for r in rows]
    if len(set(v)) > 1: moving.append((max(abs(v[i + 1] - v[i]) for i in range(len(v) - 1)), k, v))
moving.sort(key=lambda x: (-x[0], x[1]))
print(f'moving keys: {len(moving)} of {len(allk)}')
for _, k, v in moving[:a.top]:
    print('  ' + ' -> '.join(f'{x:g}' for x in v) + '   ' + k)
ok = True
for i in range(len(rows) - 1):
    np_ = sum(1 for p in plants if rows[i][1] < p <= rows[i + 1][1])
    if not np_: continue
    for k in ('R/-1/s7590-plant:?', 'S/23/unattr'):
        d = rows[i + 1][4].get(k, 0) - rows[i][4].get(k, 0)
        print(f'control {k}: window {i}->{i+1} step {d:g} for {np_} plants (window medians; +/-1 lag)')
        if abs(d - np_) > 2: ok = False
print('control', 'PASS' if ok and plants else 'FAIL' if plants else 'NO-PLANT')
sys.exit(0 if ok and plants else 1)
