# NEXT (s7412)
HYPOTHESIS-ID: integer-64bit-gpr-emission-semantics

s7411 closed class BU (unaligned load/store macros, tools/s7411_unaligned_contract.py, H-equal, mutant control PASS x8).
Class BV: integer emission semantics on 64-bit GPRs. Emitted op counts (comment lines): slti 1139, sltu 889, sltiu 880,
slt 757, mult 468, mflo 458, mfhi 214, div 92, dsll 83, multu 63, divu 46, ddiv 35, dsrl32 19, dsll32 16, dsllv 10,
dmultu 8, ddivu 5, plus ~15 rare 64-bit ops (dsrav, dsra32, dsrl, dmult, daddi, mthi/mtlo, dsub(u), dsrlv, dsra, dadd(i)u).
(grep -hoE '// 0x[0-9A-F]{8}: <op> ' ../N64Recomp/RecompiledFuncs/*.c). Example: mult ->
`result = S64(S32(rs)) * S64(S32(rt)); lo = S32(result >> 0); hi = S32(result >> 32);`
1. Offline (no game run), like s7411: take each op's EMITTED C statement shape from the generator source
   (lib/N64ModernRuntime/N64Recomp/src/*.cpp instruction table, or harvest the exact text per op from RecompiledFuncs) and
   compile it with the real build recomp.h against a VR4300 model (manual: 32-bit ops sign-extend results; slt/sltu compare
   all 64 bits; div by 0 / INT_MIN/-1 hi/lo rules; dsll32 etc shift by sa+32; dsrav/dsllv use rs&63). >=1e6 random cases per
   op, with BOTH canonical (sign-extended) and non-canonical 64-bit inputs reported separately. Perturbed control per op.
2. Census: can a 32-bit op (addu/sll/slt/mult/div...) ever see a non-canonical input? Producers of non-canonical values are
   ld/ldl/ldr, dsll/dsll32/dsrl*, daddu, dmult(u)/ddiv(u) lo/hi, dmfc1. Trace each such producer's dest to its consumers
   within the function (straight-line + same-block); hardware leaves 32-bit ops on non-canonical inputs UNDEFINED, so any hit
   is either retail UB or an emitter mismatch to read by hand.
3. Hypotheses: H-equal (all canonical rows match; no non-canonical input reaches a 32-bit op), H-mism (a canonical-input
   row differs -> fix in N64Recomp emitter, regen per CLAUDE.md order), H-noncanon (a live non-canonical input reaches a
   32-bit op whose recomp result differs from VR4300 -> name the site, then a live probe on it).
