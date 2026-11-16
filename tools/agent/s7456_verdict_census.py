#!/usr/bin/env python3
"""s7456 class DL census: does a soak's rc agree with the per-arm tag= summaries its log carries?
usage: s7456_verdict_census.py [SOAK-RESULTS.md] [--since 20261101]
Per run: arms (tag= lines), dead arms (alive_at_end=0), crash arms (crashlines>0), stall arms (vi_stalls30s>0),
fatal lines (fatal_patterns.txt). Classes: agree, rc-false-fail (rc!=0, every arm alive/clean, 0 fatal),
rc-false-pass (rc==0 but some arm dead/crashed or fatal>0), no-summary (log has no tag= line)."""
import re, sys, os
res = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else 'scratch/agent/SOAK-RESULTS.md'
since = sys.argv[sys.argv.index('--since')+1] if '--since' in sys.argv else '20261101'
pats = [re.compile(l.strip()) for l in open(os.path.join(os.path.dirname(__file__), 'fatal_patterns.txt')) if l.strip()]
def f(s, k):
    m = re.search(r'(?:^|\s)' + k + r'=(\S+)', s); return m.group(1) if m else None
cnt = {}
for line in open(res, errors='replace'):
    p = [x.strip() for x in line.split('|')]
    if len(p) < 5 or not p[2].startswith('rc=') or p[0][:8] < since: continue
    rc = p[2][3:].split()[0]
    if 'VOID' in p[2] or rc == 'SYNTAX': continue
    log = p[4]
    if not os.path.isfile(log): cls = 'log-missing'; arms = dead = crash = stall = fat = '-'
    else:
        txt = open(log, errors='replace').read().splitlines()
        tags = [l for l in txt if re.match(r'\s*tag=', l)]
        fat = sum(1 for l in txt if any(q.search(l) for q in pats))
        arms = len(tags)
        dead = sum(1 for t in tags if f(t, 'alive_at_end') != '1')
        crash = sum(1 for t in tags if (f(t, 'crashlines') or '0') not in ('0',))
        stall = sum(1 for t in tags if (f(t, 'vi_stalls30s') or '0') not in ('0',))
        bad = dead + crash + stall + fat
        if not tags: cls = 'no-summary'
        elif rc == '0' and bad == 0: cls = 'agree'
        elif rc != '0' and bad > 0: cls = 'agree'
        elif rc != '0': cls = 'rc-false-fail'
        else: cls = 'rc-false-pass'
    cnt[cls] = cnt.get(cls, 0) + 1
    print(f'{p[0]:16} {p[1][:34]:34} rc={rc:4} arms={arms} dead={dead} crash={crash} stall={stall} fatal={fat} -> {cls}')
print('TOTAL', ' '.join(f'{k}={v}' for k, v in sorted(cnt.items())))
