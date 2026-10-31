#!/usr/bin/env python3
"""Self/inclusive sample counts per function for one thread of a macOS `sample` report.
usage: sample_self.py report.txt "Gfx Thread" [topN]"""
import re, sys, collections
path, thread = sys.argv[1], sys.argv[2]
top = int(sys.argv[3]) if len(sys.argv) > 3 else 40
lines = open(path, errors='replace').read().splitlines()
start = next(i for i, l in enumerate(lines) if re.match(r'\s+\d+ Thread_\d+.*' + re.escape(thread), l))
rx = re.compile(r'^(\s*[+!:| ]*?)(\d+) (.+?)\s+(?:\(in [^)]*\))?\s*(?:\+ [\d,]+)?\s*\[')
nodes = []
for l in lines[start + 1:]:
    if re.match(r'\s+\d+ Thread_', l) or not l.strip():
        break
    m = rx.match(l)
    if not m:
        continue
    nodes.append((len(m.group(1)), int(m.group(2)), re.sub(r'\(.*', '', m.group(3)).strip()))
selfc, incl = collections.Counter(), collections.Counter()
for i, (d, c, name) in enumerate(nodes):
    kids = 0
    for d2, c2, _ in nodes[i + 1:]:
        if d2 <= d:
            break
        if d2 == min(x[0] for x in nodes[i + 1:i + 2]):
            kids += c2
    selfc[name] += c - kids
total = nodes[0][1] if nodes else 0
# inclusive: count each name once per root-to-leaf path (top-level occurrences only)
stack = []
for d, c, name in nodes:
    while stack and stack[-1][0] >= d:
        stack.pop()
    if name not in [s[1] for s in stack]:
        incl[name] += c
    stack.append((d, name))
print(f'thread={thread} samples={total}')
print('-- self --')
for n, c in selfc.most_common(top):
    print(f'{c:6d} {100*c/total:5.1f}% {n[:110]}')
print('-- inclusive (rs64_/s6/floor/m5/probe/getenv hooks) --')
for n, c in incl.most_common():
    if re.search(r'rs64_|s\d{4}_|floor|m5_|probe|getenv|log|printf|fwrite', n, re.I):
        print(f'{c:6d} {100*c/total:5.1f}% {n[:110]}')
