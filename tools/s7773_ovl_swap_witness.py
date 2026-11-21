#!/usr/bin/env python3
"""s7773 runtime witness for the overlay fn-pointer class: across retained game stderr logs (scratch/**/log_*.txt,
build/*.log, last --days), count overlay loads ([s7528] post idx=N: 2 mission, 3 menu, 4 cinematic), the overlay->overlay
swaps per log (a mission NPC slot handler built by .text setupNpcUpdateFunctions that outlived a mission->menu/cinematic
swap would be dispatched through get_function and abort with "Failed to find function": every such target is a start in
exactly one overlay, s7773 multi_start=0), and the abort / [missing-func] lines. Positive control: overlay loads > 0 and
--plant appends a synthetic abort line to an in-memory copy of one log, which must count."""
import argparse, glob, os, sys, time
ap = argparse.ArgumentParser(); ap.add_argument('--days', type=float, default=14); ap.add_argument('--plant', action='store_true')
a = ap.parse_args()
fs = [f for f in glob.glob('scratch/**/log_*.txt', recursive=True) + glob.glob('build/*.log')
      if os.path.isfile(f) and time.time() - os.path.getmtime(f) < a.days * 86400]
tr, fail, miss, withload, loads, swaplogs = {}, 0, 0, 0, 0, 0
for k, f in enumerate(fs):
    seq = []
    lines = open(f, errors='replace').read().splitlines()
    if a.plant and k == 0:
        lines.append('Failed to find function at 0x800DB11C')
    for l in lines:
        if l.startswith('[s7528] post idx='):
            seq.append(int(l.split('idx=')[1].split()[0]))
        elif 'Failed to find function' in l:
            fail += 1
        elif '[missing-func]' in l:
            miss += 1
    withload += bool(seq); loads += len(seq)
    ov = [s for s in seq if s >= 2]
    sw = [(x, y) for x, y in zip(ov, ov[1:]) if x != y]
    swaplogs += bool(sw)
    for p in sw:
        tr[p] = tr.get(p, 0) + 1
name = {2: 'mission', 3: 'menu', 4: 'cinematic'}
print('WITNESS logs=%d with_loads=%d loads=%d swap_logs=%d swaps=%s fail=%d missing_func=%d' % (
    len(fs), withload, loads, swaplogs, ','.join('%s>%s:%d' % (name.get(x, x), name.get(y, y), c) for (x, y), c in sorted(tr.items())) or '-', fail, miss))
ok = loads > 0 and (fail == 1 if a.plant else fail == 0 and miss == 0)
print('RESULT %s' % ('PASS' if ok else 'FAIL'))
sys.exit(0 if ok else 1)
