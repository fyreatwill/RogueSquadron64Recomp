# NEXT (s7414)
HYPOTHESIS-ID: fp-compare-emission-semantics

s7413 closed class BW (tools/s7413_aligned_ldst.py: 58,654 emitted load/store forms, 0 MISM, CONTROL PASS x8).
Class BX: FP compare + FP branch emission. c.f/un/eq/ueq/olt/ult/ole/ule/sf/ngle/seq/ngl/lt/nge/le/ngt .s/.d -> the
emitted `c1cs = ...` lowering, then bc1t/bc1f/bc1tl/bc1fl reading c1cs (s4837 covered only the delay-slot shape of the
likely forms, not the condition value).
1. Offline, the s7412/s7413 way: harvest every c.cond.fmt site + its statement verbatim (skip the same pass-through
   prefixes as s7413 and require operand match against the disasm), compile against the real header -O2, and drive with
   float/double operands including +-0, denormals, +-inf, qNaN and sNaN, equal pairs and near-equal pairs.
   Model: the MIPS cond table (bit0 = unordered, bit1 = equal, bit2 = less; the signalling half only adds the invalid trap,
   which the game never enables -> value-identical). Also check the branch statements read the same variable the
   compare wrote.
2. Positive control: mutants (unordered bit dropped, i.e. `<` for `ult`; eq <-> ueq; ole -> olt) must flag only their own
   conds.
3. Hypotheses: H-equal (0 MISM) / H-nan (a C operator differs from the MIPS cond on NaN, e.g. !(a>=b) vs a<b) /
   H-fmt (.d compare reads the .s view or the wrong FR slot) / H-stale (a bc1x reads a c1cs not written on that path).
