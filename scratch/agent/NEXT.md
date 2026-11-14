# NEXT (s7348): idiom-class audit - class Y, integer division / modulo by a guest-derived divisor with no zero check
HYPOTHESIS-ID: host-int-div-zero
Context: s7347 closed class X (tools/s7347_f2i_census.py: 233 float conversions, 7 sink sites, 0 open; rs64_s7233_cell NaN bin fixed).
Sibling idiom: `a / b` or `a % b` with integer type where b comes from guest data (VI width / xScale / yScale registers, RDP image
width, tile line / stride, task sizes, ucode fields, MEM_* reads) or from a float rounded to int (e.g. rt64_framebuffer_renderer
`coord % std::lround(resScale[1])`), with no `b == 0` / `b > 0` / max(1, b) check before. x86 raises SIGFPE; arm64 udiv/sdiv return 0
silently (wrong value, no crash). INT_MIN / -1 is also UB.
Hypotheses: H-safe (every divisor is a constant, a sizeof, nonzero by construction, or checked), H-diag (only gated probes),
H-zero (a default-on guest-derived divisor can be 0: real defect, fix with a guard).
Method: new tools/s7348_div_census.py on the s7343 scope (s43.files_in_scope); reuse s7346 idents()/member_types()/hdr_text() and s7347
is_float() to exclude float division. Sites: `/` or `%` (not `//`, not `/=` in comments, not float operands) whose right operand is
not a literal/sizeof/constexpr (s42.ev). Classes: K constant, NZ divisor checked (`if (!b)`, `b == 0`, `b > 0`, `b != 0`, max(1, ..),
`?:` guard) before the op in the function, BC nonzero by construction (`1 << n`, `x | 1`, +1 of an unsigned), G/D/P/C, H hand,
B default-on guest divisor unchecked. Controls: planted `uint32_t w = task->width; return off / w;` ('?'), checked twin (NZ),
shift twin (BC), gated twin (G).
Runtime only if a B site exists: fix + standalone control, then `env SECS=260 zsh scratch/s7326/run.zsh s7348_dd8 ''`.
Exit: PORTING-STATE s7348, CURRENT-TRUTH item 27m -> closed/fixed, commit.
