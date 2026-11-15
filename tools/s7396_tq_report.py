#!/usr/bin/env python3
"""s7396 class BF report: [s7396-tq] thread_queue_remove rows + [s7396-tq-ctl] planted control.
Usage: tools/s7396_tq_report.py <run.log> [...]. rc 0 = control PASS and no row the OLD walk would HANG/WILD on,
rc 2 = control missing/FAIL, rc 3 = live HANG/WILD rows (old walk would have hung or wild-read: H-dangle reachable)."""
import re, sys, collections
rc_all = 0
for path in sys.argv[1:]:
    txt = open(path, errors='replace').read()
    ctl = re.findall(r'^\[s7396-tq-ctl\].*$', txt, re.M)
    rows = re.findall(r'^\[s7396-tq\] (.*)$', txt, re.M)
    kinds = collections.Counter(); bad = []
    for r in rows:
        d = dict(kv.split('=', 1) for kv in r.split() if '=' in kv)
        kinds[(d['tag'], d['q'][:4] == 'RUN:' and 'RUN' or 'MQ', d['pos'], d['len'], d['old'])] += 1
        if d['old'] in ('HANG', 'WILD'):
            bad.append(r)
    cpass = bool(ctl) and all('PASS' in c for c in ctl)
    print('%s: control=%s rows=%d' % (path, 'PASS' if cpass else ('FAIL' if ctl else 'MISSING'), len(rows)))
    for k, v in sorted(kinds.items()):
        print('  tag=%-7s q=%-3s pos=%-3s len=%-3s old=%-7s n=%d' % (k + (v,)))
    for b in bad[:8]:
        print('  LIVE:', b)
    rc = 2 if not cpass else (3 if bad else 0)
    print('  VERDICT', {0: 'H-none (old walk safe on every live remove)', 2: 'NO-CONTROL',
                        3: 'H-dangle-reachable (old walk would hang/wild-read)'}[rc])
    rc_all = max(rc_all, rc)
sys.exit(rc_all)
