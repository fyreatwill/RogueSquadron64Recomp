# NEXT: owner reports first; otherwise fixup-layer statement census (every retail statement once per function)
HYPOTHESIS-ID: fixup-layer-statement-census
Context: s7089 closed the host-shim layer (ABI s7088 + results s7089, tools/s7089_shim_result_census.py) and found that
OUR fixup layer, not N64Recomp, had duplicated two call blocks in reapplyAudioConfig (s3531 `call + needle` rule; fixed,
tools/fixup_s7089_dupcall.py). The s7089 detector only sees duplicated `jal` comments. A duplicated or dropped
non-call statement (store, delay slot, branch) from any of the ~40k lines of fixup/apply layers would be invisible.
Unit (offline, one tool, no game run unless a live defect is found):
1. Per function, extract the guest statements N64Recomp emits (lines following each `// 0xADDR: insn` comment up to the
   next comment: assignments to ctx->rN / ctx->fN, MEM_* stores, gotos, if-heads, calls) from the pristine front-end
   pass scratch/s7082/regen and from the live ../N64Recomp/RecompiledFuncs (+ build/factor5_ucode if it has a pristine).
2. Normalise known instrumentation wrappers (s4307 synth-read `{ uint32_t s4575_a = ...; X; rs64_... }`, S5798 store
   wrappers `{ MEM_W(..) = ..; RS64_S5798_ST(..); }`, `if (__builtin_expect(g_rs64_store_diag,0)) ...` lines, PATCH-tagged
   lines) back to the bare statement, then compare the per-address statement multisets.
3. Classify every address whose live count != pristine count: {instrumentation-only, intended PATCH (tag names it),
   duplicate, dropped}. A duplicate/dropped without a PATCH tag naming the change is a defect: fix in the fixup that wrote it.
Controls: positive = the pre-s7089 reapplyAudioConfig (scratch/s7089/funcs_24.pre.c.gz) must show 0x80091CB0 and 0x80091CBC
as duplicates; negative = a function with no patches (pick one from the pristine/live diff with zero changed lines) gives 0.
Expected outcomes: 0 untagged dup/drop (closes the fixup layer); or N sites, each one a named writer + fix + rebuild + L6 boot.
Live check recipe (s7089): `zsh scratch/s7089/run.zsh` (L6 dd1 4:3 FPS60, boot to flight).
