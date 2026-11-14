# NEXT (s7346): idiom-class audit - class W, signed lengths reaching size_t sinks
HYPOTHESIS-ID: host-signed-len-sinks
Context: s7345 closed class V (tools/s7345_mul_census.py: 1402 product sites, 0 open). Sibling idiom: a length held in a signed
type (`int n`, `int32_t len`, `s32`, ptrdiff of guest values, `end - start` of int operands) is checked only from above
(`if (n > cap) return;`), so a negative n passes and is converted to size_t / uint32 at a memcpy/memset/memmove/resize/new/
loop bound/fwrite, becoming ~2^32/2^64.
Hypotheses: H-safe (every signed length is checked `n < 0` / `n <= 0`, or is non-negative by construction: unsigned source,
masked, loop count), H-diag (only gated probes), H-neg (default-on signed length from guest data, upper-bound-only check: real
defect, fix with `if (n < 0 || n > cap)` + reject log).
Method: new tools/s7346_signed_len_census.py on the s7343 scope; reuse s7345 width()/census scaffolding, s7344 decl(), s7343
args_of() to pull the length argument of each sink. Sites: sink length args (memcpy/memset/memmove 3rd arg, resize/reserve/new[]
arg, fwrite size*count, for-bound `i < n`) whose expression involves a variable declared int/int32_t/s32/int16_t/long/ptrdiff_t
or a subtraction. Classes: U unsigned type; LB lower bound checked earlier (`n < 0`, `n <= 0`, `n >= 0 &&`, max(0, ..)); MSK
masked/narrow-unsigned source; K constant; G/D/P/C; B default-on, guest-derived, no lower bound. Controls: planted
`int n = (int)task->size; if (n > 0x1000) return; memcpy(b, rdram, n);` ('?'), lower-bounded twin ('LB'), unsigned twin ('U'),
gated twin ('G').
Runtime only if a B site exists: fix + selftest, then `env SECS=260 zsh scratch/s7326/run.zsh s7346_dd8 ''`.
Exit: PORTING-STATE s7346, CURRENT-TRUTH item 27k -> closed/fixed, commit.
