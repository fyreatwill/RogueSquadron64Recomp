#!/usr/bin/env python3
"""Join [pcm-boundary-source] and [pcm-boundary-consumer] rows from a game log.

Usage: python3 -I tools/pcm_join.py <log>
Reports, per VI width, row counts, how many buffers are fully nonzero /
all-zero / partial at each point, byte-level entropy of distinct hashes, and
whether source and consumer FNV hashes agree (n-th row of each width).
"""
import collections
import re
import sys

ROW = re.compile(
    r'\[pcm-boundary-(source|consumer)\] n=(\d+) phase=(\d+) width=(\d+).*?'
    r'rdram=(0x\w+) samples=(\d+) bytes=(\d+) fnv=(0x\w+) nz=(\d+)')

src, con = {}, {}
for line in open(sys.argv[1], errors='ignore'):
    m = ROW.match(line)
    if not m:
        continue
    kind, n, _ph, w, addr, samples, nbytes, fnv, nz = m.groups()
    (src if kind == 'source' else con)[(w, int(n))] = (
        addr, int(samples), fnv, int(nz), int(nbytes))

for name, d in (('source', src), ('consumer', con)):
    c = collections.Counter()
    for (w, _n), v in d.items():
        c[(w, 'rows')] += 1
        c[(w, 'allzero' if v[3] == 0 else 'full' if v[3] == v[4] else 'partial')] += 1
    hashes = collections.Counter(w for (w, _), v in d.items())
    print(name, dict(c), 'distinct fnv:',
          {w: len({v[2] for (ww, _), v in d.items() if ww == w}) for w in hashes})
common = set(src) & set(con)
print('fnv match', sum(1 for k in common if src[k][2] == con[k][2]), 'of', len(common))
for k in list(src)[:3] + [k for k in src if k[0] == '512'][:3]:
    print(k, src[k], con.get(k))
