# NEXT (s7605)
HYPOTHESIS-ID: host-fpr-view-census

Class RA closed s7604 (tools/s7604_ra_census.py, 0 open, controls 6/6, witness 12/12; recomp_alloc dead-path fix). Next idiom
class FR: host code reading or writing a GUEST FPR (ctx->fN). ~21 sites in src/ + librecomp + ultramodern (grep 'ctx->f[0-9]').
Contract: o32 float args arrive in f12 (a0) and f14 (a1), a double in f12/f14 as .d; float return in f0 .fl, double in f0 .d.
The view used (.fl / .d / .u32l / .u32h) must match the retail prototype of the stubbed function, and the recompiler's FR mode
(check recomp.h fpr union + N64Recomp's mips3_float_mode / odd-register handling: does an FR=0 double live in f12 alone or in
the f12/f13 pair as two u32 halves?). helpers.hpp _arg<N,float> only admits index 0 (f12) and _arg_float_a1 reads a1 as u32
bits: check that matches o32 (float a1 after a float a0 is f14, after an int a0 it is a1 in a gpr).
Per site verdict: ok-proto (view matches the retail prototype, named), ok-diag (env-gated log), BAD (wrong register or view).
Hypotheses: H-clean, H-bad-gated, H-bad-live (a default-path float stub reads the wrong half/register -> wrong value; runtime
witness: call it with a known float from a level and compare).
Tool: tools/s7605_fr_census.py --controls: (1) plant `ctx->f0.d = x` in a stub whose prototype returns float -> OPEN;
(2) plant a read of f13 as the second float arg -> OPEN; (3) drop a row -> OPEN; (4) make _arg_float_a1 read r6 -> OPEN.
Second source: a witness .cpp against the real recomp.h union (as tools/s7604_ra_witness.cpp).
Never touch build/saves; never clear ROGUESQ_NO_SAVE_WRITE.
