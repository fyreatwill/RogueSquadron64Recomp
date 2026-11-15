#!/usr/bin/env python3
"""s7397 class BG runtime report over ROGUESQ_S7397_TM=1 logs: per timer struct sets / live re-arms / stops / fires, plus the
_CTL line. Exit 0 = control PASS (or absent with --no-ctl) and H-none (no live re-arm, no stop of a live timer with a fire after
it); 1 = control fail; 2 = H-rearm or H-stop-late seen. Fake control structs (0x9FFE1000-0x9FFE105F) are excluded.
Usage: tools/s7397_timer_report.py <run.log> [--no-ctl]"""
import re, sys, collections
log = sys.argv[1]; noctl = '--no-ctl' in sys.argv
sets = collections.Counter(); rearm = collections.Counter(); stops = collections.Counter(); fires = {}; info = {}; ctl = None
for ln in open(log, errors='replace'):
    if ln.startswith('[s7397-tm-ctl]'):
        ctl = ln.strip()
        continue
    m = re.match(r'\[s7397-tm\] (set|stop|fire) t=([0-9A-F]{8}) (.*)', ln)
    if not m:
        continue
    k, t, rest = m.group(1), int(m.group(2), 16), m.group(3)
    if 0x9FFE1000 <= t < 0x9FFE1060:
        continue
    if k == 'set':
        sets[t] += 1; info[t] = rest
        if 'live=1' in rest or re.search(r'live=[2-9]', rest):
            rearm[t] += 1
    elif k == 'stop':
        stops[t] += 1
    else:
        fires[t] = int(re.search(r'n=(\d+)', rest).group(1))
for t in sorted(set(sets) | set(stops) | set(fires)):
    print('t=%08X sets=%d live_rearms=%d stops=%d fires>=%d  last_set: %s' % (t, sets[t], rearm[t], stops[t], fires.get(t, 0), info.get(t, '')))
print('control:', ctl or 'ABSENT')
cpass = ctl is not None and ctl.endswith('PASS')
nre = sum(rearm.values())
v = 'H-rearm' if nre else 'H-none'
print('structs=%d sets=%d live_rearms=%d stops=%d VERDICT %s' % (len(set(sets) | set(fires)), sum(sets.values()), nre, sum(stops.values()), v))
sys.exit(0 if (cpass or noctl) and v == 'H-none' else (1 if not (cpass or noctl) else 2))
