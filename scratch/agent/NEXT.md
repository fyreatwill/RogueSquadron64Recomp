# NEXT (s7604)
HYPOTHESIS-ID: host-register-read-truncation-census

Class RX closed s7603 (tools/s7603_rx_census.py, 0 open, controls 5/5, witness 9/9). Next idiom class RA: host code READING a
guest register. Guest gpr values are sign-extended 64-bit: a KSEG0 pointer in a0 is 0xFFFFFFFF80114388, not 0x80114388. Host
code that uses ctx->rN (N in 4..7, 2, 3, 29, 31, s-regs in hooks) or a gpr-typed local in a compare against a u32 constant
(`ctx->r4 == 0x80114388u` is always false), as a host array index / pointer offset (rdram + ctx->r4), in a 64-bit division,
shift right, or a size_t length without truncating it first is wrong. MEM_W/MEM_B/TO_PTR macros mask the address themselves
(check how: ADD32 / (int32_t) / & 0x1FFFFFFF in recomp.h) -> ok-macro.
Scope: src/, librecomp/src, ultramodern/src, tests skipped; enumerate every `ctx->r[0-9]+` READ (not the LHS of `=`), plus
`_arg<N, T>` (helpers.hpp: check it truncates to T).
Per site verdict: ok-cast ((uint32_t)/(int32_t)/(s32)/(u32) applied, or passed to a parameter of 32-bit type), ok-macro
(MEM_*/TO_PTR/ADD32 operand), ok-copy (stored back to a gpr), ok-zero (compared with 0 / nonzero test), ok-sext-compare (compared
with a (gpr)(int32_t) constant or another gpr), BAD (64-bit use of a value whose upper half is sign fill).
Hypotheses: H-clean, H-bad-gated (BAD only in env-gated diagnostics: fix them, they print or match wrong), H-bad-live (a
default-path compare/index never matches -> real behavioural bug; runtime witness at a level).
Tool: tools/s7604_ra_census.py --controls: (1) plant `if (ctx->r4 == 0x80114388u)` in a copy of upstream_compat.cpp -> OPEN;
(2) plant `rdram[ctx->r5]` -> OPEN; (3) drop a row -> OPEN; (4) make _arg drop its truncation in a copy of helpers.hpp -> OPEN.
For BAD rows: known-value witness (sign-extended a0 into the real function), then fix; a default-path fix needs a level run.
Never touch build/saves; never clear ROGUESQ_NO_SAVE_WRITE.
