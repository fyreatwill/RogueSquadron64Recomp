# NEXT (s7347): idiom-class audit - class X, float-to-integer conversions of guest floats reaching index/size sinks
HYPOTHESIS-ID: host-float-to-int-sinks
Context: s7346 closed class W (tools/s7346_signed_len_census.py: 1322 sinks, 0 open; RT64 CommandWarning::format fixed).
Sibling idiom: a guest float (RDRAM/DMEM-read float, guest vertex/matrix/camera value, FPR ctx->f*) converted to an integer with
`(int)f`, `int i = f`, static_cast<int>, lround/lrint/floor-then-cast, then used as an array index, a memcpy/resize length, a loop
bound or a pointer offset. NaN / +-inf / |f| >= 2^31 is UB in C++; arm64 fcvtzs saturates (NaN -> 0, huge -> INT_MAX/INT_MIN), so a
NaN camera value could become INT_MIN as an index.
Hypotheses: H-safe (every such conversion is clamped / isfinite-checked / the result is clamped before the sink), H-diag (only
gated probes / logging), H-ub (default-on guest float -> int -> sink with no clamp: real defect, fix with an isfinite + clamp helper).
Method: new tools/s7347_f2i_census.py on the s7343 scope; reuse s7346 idents()/member_types()/hdr_text() for types and s7345
FLOATT/FLOATCALL for float detection. Sites: casts `(int|int32_t|uint32_t|s32|u32|size_t|long)\s*\(?expr` / static_cast<int..>
/ lround/lrint/(int)floor/ceil, and int-typed locals assigned a float expression, whose result feeds a sink (index `[..]`, memcpy
len, resize, for bound, pointer +) on the same line or a later line of the function (s7345 sink_use()). Classes: CL clamped
(std::clamp/min/max on the float before or the int after, or an `if (x < 0 || x >= N)` before the sink), FIN isfinite/isnan
check, HOST host-only float (config, time, resolution scale), G/D/P/C, B default-on guest float unclamped. Controls: planted
`float f = guest_f(); int i = (int)f; tab[i] = 1;` ('?'), clamped twin ('CL'), isfinite twin ('FIN'), gated twin ('G').
Runtime only if a B site exists: fix + selftest, then `env SECS=260 zsh scratch/s7326/run.zsh s7347_dd8 ''`.
Exit: PORTING-STATE s7347, CURRENT-TRUTH item 27l -> closed/fixed, commit.
