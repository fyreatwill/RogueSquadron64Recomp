#!/usr/bin/env python3
"""s7318 spill-holder-field-compare: runtime classifier for the class-B field-order compares of s7317.

tools/s7318_bcmp_sites.txt (generated once from tools/s7317_field_compare_census.py on the dd8 21:9 L4 holder dump) lists 182
`lw d, off(base)` -> `slt/sltu x, d, other` sites; a static pass cannot tell whether a spill pointer (0x81000000+) loaded from such
a field is ordered against a pointer into the same block (order = retail order) or against a heap pointer / bound (order can differ
from retail's all-heap layout). Before every such compare this inserts
    if (rs64_s7318_on) rs64_s7318_bcmp(idx, pc, U32(rs), U32(rt));
(measurement only, ROGUESQ_S7318_BCMP=1|<path>; classifier in src/main/upstream_compat.cpp next to the s7317 alloc map).
Delay-slot copies of a compare get the hook too (one count per executed copy). Usage: apply_s7318_bcmp_probe.py [RecompiledFuncs dir]"""
import sys, pathlib, re
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s7318 bcmp"
SITES = pathlib.Path(__file__).resolve().parent / "s7318_bcmp_sites.txt"
R = {"$zero": 0, "$at": 1, "$v0": 2, "$v1": 3, "$a0": 4, "$a1": 5, "$a2": 6, "$a3": 7, "$t0": 8, "$t1": 9, "$t2": 10, "$t3": 11,
     "$t4": 12, "$t5": 13, "$t6": 14, "$t7": 15, "$s0": 16, "$s1": 17, "$s2": 18, "$s3": 19, "$s4": 20, "$s5": 21, "$s6": 22,
     "$s7": 23, "$t8": 24, "$t9": 25, "$k0": 26, "$k1": 27, "$gp": 28, "$sp": 29, "$fp": 30, "$ra": 31}
sites = {}
for ln in SITES.read_text().splitlines():
    if ln.startswith("#") or not ln.strip(): continue
    idx, pc = ln.split()[:2]
    sites.setdefault(pc[2:].upper(), int(idx))
files = sorted(D.glob("funcs_*.c"))
if any(TAG in f.read_text(errors="surrogateescape") for f in files):
    print("already applied"); sys.exit(0)
pat = re.compile(r"^(\s*)// 0x([0-9A-F]{8}): (sltu?)\s+(\$\w+), (\$\w+), (\$\w+)\n", re.M)
hit = {}
for f in files:
    t = f.read_text(errors="surrogateescape")
    def sub(m):
        pc = m.group(2)
        if pc not in sites: return m.group(0)
        hit[pc] = hit.get(pc, 0) + 1
        a, b = R[m.group(5)], R[m.group(6)]
        return m.group(0) + "%s{ extern int rs64_s7318_on; extern void rs64_s7318_bcmp(int, uint32_t, uint32_t, uint32_t); if (rs64_s7318_on) rs64_s7318_bcmp(%d, 0x%su, U32(ctx->r%d), U32(ctx->r%d)); } /* %s */\n" % (m.group(1), sites[pc], pc, a, b, TAG)
    n = pat.sub(sub, t)
    if n != t: f.write_text(n, errors="surrogateescape")
miss = sorted(set(sites) - set(hit))
assert not miss, ("sites not found", miss)
print("s7318 bcmp: %d sites, %d hooks (delay-slot copies included)" % (len(hit), sum(hit.values())))
