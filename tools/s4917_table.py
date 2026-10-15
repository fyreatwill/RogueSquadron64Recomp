#!/usr/bin/env python3
"""s4917: per-VI-handler-iteration ordering table. Usage: s4917_table.py run.log
An iteration = events from one `recv-vi` mark to the next. For each iteration prints the compact event
sequence (tid:tag) and classifies by the psrr-bf20-ret result. Answers: does a non-handler thread's
slot-byte store (sb ... v=04) land between the handler's own slot stores and psrr-entry?"""
import re, sys
from collections import Counter

RX = re.compile(r'\[s4913\] k=(\d+) t=([\d.]+) tid=(\d+) (.*?) A=(\d) B=(\d)(?: (.*))?$')
ev = []
for l in open(sys.argv[1]):
    m = RX.match(l.rstrip())
    if m:
        ev.append((int(m[1]), float(m[2]), int(m[3]), m[4]))

iters, cur = [], None
for e in ev:
    if e[3] == 'recv-vi-ret':
        cur = []; iters.append(cur)
    elif cur is not None and e[3] not in ('recv-vi', 'recv-ack', 'recv-ack-ret'):
        cur.append(e)

# handler tid = tid that logs psrr-entry most often
tids = Counter(e[2] for e in ev if e[3] == 'psrr-entry')
htid = tids.most_common(1)[0][0] if tids else -1
print("iterations:", len(iters), "handler tid:", htid, "psrr tids:", dict(tids))
cls = Counter()
samples = {}
for it in iters:
    names = [e[3] for e in it]
    if 'psrr-entry' not in names:
        cls['no-psrr'] += 1; continue
    pi = names.index('psrr-entry')
    pre = it[:pi]
    ret = next((n for n in names if n.startswith('psrr-bf20-ret')), 'no-ret')
    foreign4 = [e for e in pre if e[2] != htid and e[3].startswith('sb') and ('a=+2' in e[3] or 'a=+3' in e[3]) and e[3].endswith('v=04')]
    own = [e for e in pre if e[2] == htid and e[3].startswith('sb')]
    foreign_after_own = [e for e in foreign4 if own and e[0] > own[0][0]]
    key = (ret, 'foreign-4-before-psrr' if foreign4 else 'no-foreign-4',
           'after-handler-stores' if foreign_after_own else '-')
    cls[key] += 1
    samples.setdefault(key, [(f"{e[2]}:{e[3]}") for e in it][:14])
for k, v in cls.most_common():
    print(v, k)
for k, s in samples.items():
    print("SAMPLE", k, " | ".join(s))
