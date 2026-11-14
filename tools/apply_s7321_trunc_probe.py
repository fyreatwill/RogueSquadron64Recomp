#!/usr/bin/env python3
"""s7321 spill-holder-pointer-trunc: runtime classifier for the class-D 24-bit truncation sites of tools/s7317_field_compare_census.py.

tools/s7321_trunc_sites.txt lists 26 `and d, s, M` / `sll+srl` sites whose kept-bit mask lacks bit 24 but keeps bits 16..21: a heap
pointer 0x80xxxxxx survives as its physical address, a spill pointer 0x81xxxxxx loses bit 24 and aliases low RDRAM (or, re-tagged
with | 0x80000000 as commitMeshDrawBatchRefs does, aliases heap). Before every such instruction this inserts
    if (rs64_s7318_on) rs64_s7318_bcmp(idx, pc, U32(src), 0x80000000u);
reusing the s7318 classifier (src/main/upstream_compat.cpp; idx 512-767 = class D; cross = the source is a spill pointer).
Measurement only: ROGUESQ_S7318_BCMP=1|<path> + ROGUESQ_S7317_ALLOCMAP=1. Usage: apply_s7321_trunc_probe.py [RecompiledFuncs dir]"""
import sys, pathlib, re
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s7321 trunc"
SITES = pathlib.Path(__file__).resolve().parent / "s7321_trunc_sites.txt"
R = {"$zero": 0, "$at": 1, "$v0": 2, "$v1": 3, "$a0": 4, "$a1": 5, "$a2": 6, "$a3": 7, "$t0": 8, "$t1": 9, "$t2": 10, "$t3": 11,
     "$t4": 12, "$t5": 13, "$t6": 14, "$t7": 15, "$s0": 16, "$s1": 17, "$s2": 18, "$s3": 19, "$s4": 20, "$s5": 21, "$s6": 22,
     "$s7": 23, "$t8": 24, "$t9": 25, "$k0": 26, "$k1": 27, "$gp": 28, "$sp": 29, "$fp": 30, "$ra": 31}
sites = {}
for ln in SITES.read_text().splitlines():
    if ln.startswith("#") or not ln.strip(): continue
    f = ln.split(); sites.setdefault(f[1][2:].upper(), (int(f[0]), R[f[2]]))
files = sorted(D.glob("funcs_*.c"))
if any(TAG in f.read_text(errors="surrogateescape") for f in files):
    print("already applied"); sys.exit(0)
pat = re.compile(r"^(\s*)// 0x([0-9A-F]{8}): (and|sll)\s+(\$\w+), (\$\w+), (\S+)\n", re.M)
hit = {}
for f in files:
    t = f.read_text(errors="surrogateescape")
    def sub(m):
        pc = m.group(2)
        if pc not in sites: return m.group(0)
        hit[pc] = hit.get(pc, 0) + 1; idx, r = sites[pc]
        return m.group(0) + "%s{ extern int rs64_s7318_on; extern void rs64_s7318_bcmp(int, uint32_t, uint32_t, uint32_t); if (rs64_s7318_on) rs64_s7318_bcmp(%d, 0x%su, U32(ctx->r%d), 0x80000000u); } /* %s */\n" % (m.group(1), idx, pc, r, TAG)
    n = pat.sub(sub, t)
    if n != t: f.write_text(n, errors="surrogateescape")
miss = sorted(set(sites) - set(hit))
assert not miss, ("sites not found", miss)
print("s7321 trunc: %d sites, %d hooks (delay-slot copies included)" % (len(hit), sum(hit.values())))
