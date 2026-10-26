"""Summarise [celltest] lines: per arm, pass/fail counts, r2 values, d2 of passing/failing cells, per-sweep pass count."""
import re, sys, statistics as st
from collections import Counter
rx = re.compile(r'\[celltest\] n=(\d+) cell=0x([0-9A-F]+) d2=(\S+) r2=(\S+) pass=(\d)')
for path in sys.argv[1:]:
    rows = [(int(m[1]), m[2], float(m[3]), float(m[4]), int(m[5])) for l in open(path, errors='replace') if (m := rx.search(l))]
    import os
    rows = [r for r in rows if r[0] >= int(os.environ.get('NMIN', '40000'))]
    r2c = Counter(round(r[3], 1) for r in rows)
    p = [r for r in rows if r[4]]; f = [r for r in rows if not r[4]]
    print(path.split('/')[-2], 'tests', len(rows), 'pass', len(p), 'fail', len(f))
    print('  r2 top', r2c.most_common(4))
    if p: print('  pass d2 max %.1f med %.1f' % (max(r[2] for r in p), st.median(r[2] for r in p)))
    if f: print('  fail d2 min %.1f med %.1f' % (min(r[2] for r in f), st.median(r[2] for r in f)))
    print('  distinct cells', len({r[1] for r in rows}))
