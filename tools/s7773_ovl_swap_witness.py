#!/usr/bin/env python3
"""s7773 runtime witness for the overlay fn-pointer class: across retained game stderr logs (scratch/**/log_*.txt,
build/*.log, last --days), count overlay loads ([s7528] post idx=N: 2 mission, 3 menu, 4 cinematic), the overlay->overlay
swaps per log (a mission NPC slot handler built by .text setupNpcUpdateFunctions that outlived a mission->menu/cinematic
swap would be dispatched through get_function and abort with "Failed to find function": every such target is a start in
exactly one overlay, s7773 multi_start=0), and the abort / [missing-func] lines. Positive control: overlay loads > 0 and
--plant appends a synthetic abort line to an in-memory copy of one log, which must count.
s7803: also reads the zstd'd retained logs (log_*.txt.zst via rs64_zopen; --raw-only = the s7773 file set, which saw 99 raw
logs while 777 retained ones were .zst); --days 0 = no age limit. Prints the raw/zst split."""
import argparse, glob, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rs64_zopen import zopen
ap = argparse.ArgumentParser(); ap.add_argument('--days', type=float, default=14); ap.add_argument('--plant', action='store_true')
ap.add_argument('--raw-only', action='store_true')
a = ap.parse_args()
pats = ['scratch/**/log_*.txt', 'build/*.log'] + ([] if a.raw_only else ['scratch/**/log_*.txt.zst', 'build/*.log.zst'])
fs = sorted(set(f for p in pats for f in glob.glob(p, recursive=True)
      if os.path.isfile(f) and (a.days <= 0 or time.time() - os.path.getmtime(f) < a.days * 86400)))
nz = sum(f.endswith('.zst') for f in fs)
tr, fail, miss, withload, loads, swaplogs = {}, 0, 0, 0, 0, 0
for k, f in enumerate(fs):
    seq = []
    try:
        lines = zopen(f).read().splitlines()
    except Exception as e:  # a truncated .zst is reported, not fatal
        print('UNREADABLE %s %s' % (f, type(e).__name__)); continue
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
print('INPUT raw=%d zst=%d days=%s' % (len(fs) - nz, nz, a.days))
print('WITNESS logs=%d with_loads=%d loads=%d swap_logs=%d swaps=%s fail=%d missing_func=%d' % (
    len(fs), withload, loads, swaplogs, ','.join('%s>%s:%d' % (name.get(x, x), name.get(y, y), c) for (x, y), c in sorted(tr.items())) or '-', fail, miss))
ok = loads > 0 and (fail == 1 if a.plant else fail == 0 and miss == 0)
print('RESULT %s' % ('PASS' if ok else 'FAIL'))
sys.exit(0 if ok else 1)
