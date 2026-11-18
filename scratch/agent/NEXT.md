# NEXT (s7603)
HYPOTHESIS-ID: host-register-write-sign-extension-census

Class TP closed s7602 (tools/s7602_tp_census.py, 144 views, 0 open, controls 5/5). Next idiom class RX: host code writing a
value into a guest register. MIPS64 contract: a 32-bit result in a gpr must be sign-extended to 64 bits (recompiled code does
64-bit compares/adds on gpr; a zero-extended 0x80xxxxxx pointer or a negative s32 stored as 0x00000000FFFFFFFF breaks slt/beq
and address math that is not masked). s4884 fixed one generated idiom (zero-extended `ctx->rN = 0x80000000u`); s7087 osGetCount.
Scope: `ctx->rN = ...`, `(&ctx->r4)[i] = ...`, `_return<T>(ctx, v)` (helpers.hpp: check how it extends), ctx->f0/f2 for float
returns, r2/r3 for 64-bit returns (osGetTime: r2 = hi sign-extended, r3 = lo sign-extended), in src/, librecomp/src,
ultramodern/src (127 sites by grep `ctx->r[0-9]+\s*=[^=]|_return<`), skip tests. Also host stubs that return nothing but the
guest expects v0 (void _recomp with a non-void retail prototype -> stale r2).
Per site verdict: ok-sext (value is (gpr)(int32_t)x / s32 / int / literal < 0x80000000), ok-small (provably 0..0x7FFFFFFF),
ok-64 (value really 64-bit and the guest consumes it as such), consumer (guest only uses low 32 bits, named), BAD.
Hypotheses: H-clean, H-bad (a zero-extended negative / KSEG0 value reaches a guest compare), H-dead (bad sites only in
unreached stubs).
Tool: tools/s7603_rx_census.py --controls: (1) plant `ctx->r2 = (uint32_t)0x80001000u;` in a copy of a librecomp file -> OPEN;
(2) plant a void _recomp for a retail function that returns s32 (pick one from the symbol table) -> OPEN; (3) drop a row -> OPEN.
Runtime witness for any BAD row: known-value host unit (call the _recomp with a ctx, check r2 high word), then a level run if live.
Never touch build/saves; never clear ROGUESQ_NO_SAVE_WRITE.
