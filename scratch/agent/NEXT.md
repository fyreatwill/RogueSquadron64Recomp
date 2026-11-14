# NEXT (s7361): idiom-class audit - class AL, unvalidated guest pointer args in live host exports
HYPOTHESIS-ID: host-export-guest-ptr
Context: s7360 closed class AK (guest string reads: 1 dead site, hardened). Its second line listed the 57 host-defined *_recomp
exports the generated game actually calls (scratch/s7360/host_exports.txt; regenerate with the python in PORTING-STATE s7360).
Idiom (class AL): a live export that dereferences a guest-supplied pointer arg (`_arg<N, T*>(rdram, ctx)`, TO_PTR(T, ctx->rN),
MEM_W/MEM_H/MEM_B(off, ctx->rN), PTR(T)) without checking it is a sign-extended KSEG0 address with [p, p+sizeof) < 8 MB top.
A null / KUSEG / junk pointer there reads or writes host memory outside rdram (silent corruption, not a guest fault).
Hypotheses: H-safe (every live deref is validated or the arg is provably a static guest object), H-trust (derefs are unchecked
but every call site passes a static/stack guest address: classify by reading the callers in RecompiledFuncs), H-hole (a live
export derefs an arg a caller can pass as null/computed junk: fix with a range check that returns the OS error code).
Method: tools/s7361_exportptr_census.py over the 57 exports' bodies (+ helpers they call in librecomp/ultramodern); per deref
row CHECKED / STATIC-CALLERS (list caller arg provenance) / B. Planted controls per form. Second line: for each B, an ASan
harness like tools/s7360_rdbsend_ctl.sh (pre over-read/over-write, post rejected). Then 260 s dd8 smoke:
`env SECS=260 zsh scratch/s7326/run.zsh s7361_dd8 ''`.
Exit: PORTING-STATE s7361, CURRENT-TRUTH item 27z -> closed, commit; any lib/ edit -> ./submodule-patches/export.sh first.
