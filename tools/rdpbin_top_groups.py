#!/usr/bin/env python3
"""Rank rdpbin_tri_colors.py output: per-ord totals and top-N groups by tri count.
Usage: rdpbin_top_groups.py colors.txt [ord] [N=12]"""
import re, sys, collections
tot = collections.Counter(); rows = collections.defaultdict(list)
for l in open(sys.argv[1]):
    m = re.match(r'ord=(\d+) .* n=(\d+) meanRGB=', l)
    if m: tot[int(m[1])] += int(m[2]); rows[int(m[1])].append((int(m[2]), l.strip()))
print('ord totals', dict(sorted(tot.items())))
if len(sys.argv) > 2:
    for n, l in sorted(rows[int(sys.argv[2])], reverse=True)[:int(sys.argv[3]) if len(sys.argv) > 3 else 12]: print(l[:230])
