#!/usr/bin/env python3
"""s4979: two-source check of voice kind (+0x6D) / flag (+2 bit0) at init.

musyxInitVoiceFromSample (0x80092234-0x80092268) copies desc+0x18 to voice+0x6D
and sets voice flag bit0 only when (desc+4 & 0xF0000000) != 0x80000000.
Port side: histogram [init-desc] rows by (desc, d04 top nibble, d18).
Retail side: from a rs64_oracle --watch-pc log containing 0x800921e8 and
0x800901c0 exec rows, report the first renders after each init from a given
desc; flag clear (v0==0 at 0x800901c0) means 0x800903F0 is unreachable.

usage: voice_kind_crosscheck.py --port LOG [LOG...] --retail LOG [--desc 0x8011c820]
"""
import argparse, collections, re

ap = argparse.ArgumentParser()
ap.add_argument("--port", nargs="*", default=[])
ap.add_argument("--retail")
ap.add_argument("--desc", default="0x8011c820")
a = ap.parse_args()

c = collections.Counter()
for f in a.port:
    for l in open(f, errors="replace"):
        if l.startswith("[init-desc]"):
            m = re.search(r"desc=(0x\w+) d00=\w+ d04=(0x\w+).*d18=(0x\w+)", l)
            if m:
                c[(m.group(1), hex(int(m.group(2), 16) >> 28), m.group(3))] += 1
for k, v in c.most_common():
    print("port", v, k)

if a.retail:
    rows = []
    for l in open(a.retail, errors="replace"):
        m = re.match(r"\[hit\] x addr=\S+ pc=(0x[0-9a-f]+) .* n=(\d+) (.*)", l)
        if m:
            rows.append((int(m.group(2)), m.group(1), dict(re.findall(r"(\w+)=(0x[0-9a-f]+)", m.group(3)))))
    for n0, pc, d in rows:
        if pc == "0x800921e8" and d.get("a1") == a.desc:
            v = d["a0"]
            nxt = [(n, r) for n, p, r in rows if n > n0 and p == "0x800901c0" and r.get("s1") == v][:3]
            print("retail init n=%d voice=%s -> next renders flag v0:" % (n0, v), [r["v0"] for _, r in nxt])
