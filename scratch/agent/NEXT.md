# NEXT (s7344): idiom-class audit - class U, wrap-prone uint32 bound checks on guest-derived values
HYPOTHESIS-ID: host-wrap-prone-bound-checks
Context: s7343 closed class T (tools/s7343_buffer_copy_census.py: 466 sinks, 0 overflowing writes, one RT64 TLUT OOB read clamped).
Every clamp it credited has the form `if (a + n > LIMIT) n = LIMIT - a` or `if (a + n <= end)`. With uint32 a and n both from guest
data (DMA length, OSTask size, DL word, DPC start/end), a huge n wraps `a + n` below LIMIT, the check passes, and the copy/loop runs
with the raw n. Safe forms: `n > LIMIT - a` after `a < LIMIT`, a 64-bit sum ((uint64_t)a + n), or n pre-masked (e.g. & 0xFFF).
Hypotheses: H-safe (every check is 64-bit, pre-masked or subtractive), H-diag (wrap-prone checks are only in gated probes),
H-wrap (a default-on check on guest a/n can wrap: real defect, fix with a 64-bit sum or the subtractive form plus a log line).
Method: new tools/s7344_wrap_census.py on the s7343 scope (reuse s7343 files_in_scope(), ln_fn(), body_gated() and the s7338 classes).
Enumerate every comparison `X + Y (<|<=|>|>=) Z` and `Z (<|>) X + Y` (also `X + Y - 1`), classify:
K constant operands; W64 a (uint64_t)/(size_t on 64-bit)/`ull` cast on the sum; MSK an operand masked to <= 24 bits in the function
before the check (`&= 0xFFF`, `& 0xFFFFFF`), or a uint8/uint16 type; SUB subtractive form; G/D/P/C; B default-on with both
operands guest-derived 32-bit (say which); ? otherwise. Controls: plant `if (a + task->data_size > 0x1000) return; memcpy(..)` ('?'),
the uint64 twin ('W64'), the masked twin (`n &= 0xFFF` first, 'MSK'), a gated twin ('G').
Second part, same tool: re-run the s7338-s7342 censuses' rt64 G/D rows through s7343 body_gated(); list any that change to '?'.
Runtime only if a B site exists: build the fix, run `env SECS=260 zsh scratch/s7326/run.zsh s7344_dd8 'ROGUESQ_S7344_SELFTEST=1'`
(check screen unlocked + HID idle first) with a selftest that feeds n = 0xFFFFFFF0 once and must log the reject.
Exit: PORTING-STATE s7344, CURRENT-TRUTH item 27i -> closed/fixed, commit.
