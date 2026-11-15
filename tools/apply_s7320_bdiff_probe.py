#!/usr/bin/env python3
"""s7320 spill-holder-pointer-diff: runtime classifier for the class-C field pointer differences of s7317/s7320.

tools/s7320_bdiff_sites.txt (tools/s7317_field_compare_census.py class C on the dd8 21:9 L4 holder dump) lists 155
`lw x, off(base)` -> `subu/sub d, p, q` sites where one operand is a holder-field load and the other is non-constant. A spill pointer
(0x81000000+) minus a heap pointer (0x80xxxxxx) is >= 8 MB where retail's all-heap difference is small: any length / limit use of d
then differs from retail. Before every such subtraction this inserts
    if (rs64_s7318_on) rs64_s7318_bcmp(idx, pc, U32(rs), U32(rt));
reusing the s7318 classifier (src/main/upstream_compat.cpp; idx >= 256 = class C; cross = one spill operand, other 0x80xxxxxx).
Measurement only: ROGUESQ_S7318_BCMP=1|<path> + ROGUESQ_S7317_ALLOCMAP=1. Usage: apply_s7320_bdiff_probe.py [RecompiledFuncs dir]"""
import sys, pathlib, re
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s7320 bdiff"
SITES = pathlib.Path(__file__).resolve().parent / "s7320_bdiff_sites.txt"
R = {"$zero": 0, "$at": 1, "$v0": 2, "$v1": 3, "$a0": 4, "$a1": 5, "$a2": 6, "$a3": 7, "$t0": 8, "$t1": 9, "$t2": 10, "$t3": 11,
     "$t4": 12, "$t5": 13, "$t6": 14, "$t7": 15, "$s0": 16, "$s1": 17, "$s2": 18, "$s3": 19, "$s4": 20, "$s5": 21, "$s6": 22,
     "$s7": 23, "$t8": 24, "$t9": 25, "$k0": 26, "$k1": 27, "$gp": 28, "$sp": 29, "$fp": 30, "$ra": 31}
sites = {}
gapfn = {}
for ln in SITES.read_text().splitlines():
    if ln.startswith("#") or not ln.strip(): continue
    idx, pc = ln.split()[:2]
    sites.setdefault(pc[2:].upper(), int(idx))
    gapfn.setdefault(pc[2:].upper(), ln.split()[2] if len(ln.split()) > 2 else "")
files = sorted(D.glob("funcs_*.c"))
if any(TAG in f.read_text(errors="surrogateescape") for f in files):
    print("already applied"); sys.exit(0)
pat = re.compile(r"^(\s*)// 0x([0-9A-F]{8}): (subu?)\s+(\$\w+), (\$\w+), (\$\w+)\n", re.M)
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
# s7420: a regen with tools/func_sizes.txt sizes data_gap_* to its real (data) length, so sites the live tree decoded
# inside a data gap do not exist there; only those may be absent.
gone = [pc for pc in miss if gapfn.get(pc, "").startswith("data_gap_")]
if gone: print("s7320: %d data_gap site(s) absent from this tree (not code): %s" % (len(gone), " ".join(gone)))
miss = [pc for pc in miss if pc not in gone]
assert not miss, ("sites not found", miss)
print("s7320 bdiff: %d sites, %d hooks (delay-slot copies included)" % (len(hit), sum(hit.values())))
