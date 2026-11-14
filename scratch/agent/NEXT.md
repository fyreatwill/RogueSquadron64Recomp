# NEXT (s7352): idiom-class audit - class AC, signed 32-bit add/sub/negate overflow on guest-derived ints
HYPOTHESIS-ID: host-signed-overflow
Context: s7351 closed class AB (tools/s7351_cast_census.py: 168 sites, 0 open; RT64 framebuffer word swap fixed, latent).
Idiom: `int32_t`/`int` `a + b`, `a - b`, `-a`, `abs(a)`, `a += b` where an operand is guest-derived (RDRAM word, DL/RDP field,
OSTask field, ctx->rN, MEM_W) and the sum can leave int range. Signed overflow is UB: clang folds `x + 1 > x`, range checks and loop
trip counts on it. MIPS ADDU/SUBU wrap, so retail semantics = unsigned wrap. (Class V s7345 covered 32-bit multiply only.)
Hypotheses: H-safe (operands narrowed: int16/12-bit RDP fields sign-extended into int32 cannot overflow a sum of two; or the
arithmetic is already unsigned / int64 / float), H-diag (only gated probes), H-ub (default-on int32 sum of two full-range guest
words: fix with uint32_t arithmetic + cast, or int64).
Method: new tools/s7352_signed_census.py on the s7343 scope; reuse s7343 args_of()/ln_fn()/body_gated(), s7338 sites() C/P/G/D, s7344
CORE demotion and its NARROW/decl() helpers. Site = binary + / - (and unary -, abs) whose operand is declared int/int32_t/int64->int
narrowing and is guest-derived. Classes: NAR (operands <= 24-bit by type or mask), W64 (computed in int64/float), U (unsigned), K
(constant + small), H, B. Controls: planted `int32_t s = (int32_t)task->a + (int32_t)task->b;` ('?'), uint32 twin (U), int16 twin
(NAR), int64 twin (W64), gated twin (G).
Runtime only if a B site gets fixed: standalone UBSan control (-fsanitize=signed-integer-overflow), then
`env SECS=260 zsh scratch/s7326/run.zsh s7352_dd8 ''`.
Exit: PORTING-STATE s7352, CURRENT-TRUTH item 27q -> closed/fixed, commit.
