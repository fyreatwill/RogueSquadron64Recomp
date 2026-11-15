# NEXT (s7415)
HYPOTHESIS-ID: fp-arith-move-emission-semantics

s7414 closed class BX (tools/s7414_fp_compare.py rc 0: 2,837 c.cond sites / 282 forms 0 MISM at FZ=0, CONTROL PASS x4 +
reach plants PASS, 2,796 bc1x CLEAN). Class BY: FP arithmetic + move emission.
Census (s7414 grep): mul.s 4704, add.s 2954, sub.s 2800, mov.s 1574, div.s 1195, neg.s 720, abs.s 244, sqrt.s 95,
add.d 108, mul.d 69, sub.d 44, div.d 15, abs.d 4, mov.d 3, neg.d 1; mfc1 2962, mtc1 2418 (dmfc1/dmtc1: check).
1. Offline, the s7414 way (reuse its harvest skeleton: fnpat incl. `static void` inner bodies, mid-line disasm comments,
   pass-through prefixes CHECK_FR / PC stamp, and NEW: `NAN_CHECK(ctx->fN.fl);` lines that precede neg/abs/sqrt -- read
   NAN_CHECK's definition in recomp.h first: if it aborts/logs on NaN that is a behaviour difference to record, not skip).
   Require operand match vs disasm; compile each distinct form verbatim (-O2 -DRS64_BYTE_WATCH, force header).
2. Model: IEEE-754 binary32/64 round-to-nearest (compute in the harness with the host in FZ=0 via a separate,
   -ffp-contract=off TU, or with __int128/softfloat for div/sqrt), FR=0 register semantics for mtc1/mfc1 (sign-extend to
   64-bit GPR on mfc1), neg/abs = sign-bit ops (VR4300 neg/abs on NaN raise invalid -> trap disabled -> value: check).
   Arms: host FZ=0 and FZ=1 (default on since s7405); FZ=1 diffs on denormal in/out are expected (= retail FS=1 flush for
   outputs; inputs runtime-unreached per s7406 0 IDC) -- count separately, as s7414 did.
   Watch for: fused multiply-add contraction (-ffp-contract default on clang = on for -O2? measure: a mul.s+add.s pair in one
   C statement block could be fused by the compiler -> 1-ulp diffs vs MIPS separate rounding). Check CMakeLists flags.
3. Positive control: mutants (add->sub, mul rounding via double then float, neg as 0-x (differs on +0), abs via fabs ok vs
   x<0?-x:x (differs on -0/NaN), mfc1 zero-extend) must flag their own ops only.
4. Hypotheses: H-equal / H-contract (FMA fusion changes rounding) / H-negzero (neg/abs lowered arithmetically) /
   H-nancheck (NAN_CHECK alters control flow).
