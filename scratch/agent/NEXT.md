# NEXT work unit (s948)

Pre-run decision: source-only; do not build, run the game, or enqueue a soak.
The discriminating measurement is an exhaustive `+0x64` read/consumer
inventory: voice-handle consumers throughout select valid; an unrelated or
incompatible consumer selects mismatch; unresolved structure or flow selects
unclassified.

HYPOTHESIS-ID: m3-audio-stop-voices-by-handle-contract

Audit every generated `+0x64` read in funcs_21–23. Classify its consumer
structure and contract as voice-record handle use, unrelated fade state, or
unresolved provenance. Include record-base/slot arithmetic, register-indirect
audio-overlay edges, and companion-symbol names. No guard, behavior change,
build, or soak.

Competing hypotheses:

- H-stop-voices-by-handle-index-valid: all live `+0x64` reads consume the
  composite-handle/sentinel contract established by note-on and stop paths.
- H-stop-voices-by-handle-index-unclassified: a consumer structure or source
  remains unresolved.
- H-stop-voices-by-handle-index-mismatch: a `+0x64` read treats an unrelated
  field as a voice handle or reaches an incompatible structure.

Discriminating measurement: exhaustive `+0x64` read inventory, consumer
context, record-base/slot-flow, all audio-overlay `jalr` setup, and
companion-symbol cross-check. Voice-handle consumers throughout select valid;
an unrelated/incompatible consumer selects mismatch; unresolved structure or
flow selects unclassified.

Exact command: `rg -n -C 8 "MEM_W\\(ctx->r[0-9]+, 0X64\\)|lw +\\$[^,]+, 0x64\\(" ../N64Recomp/RecompiledFuncs/funcs_21.c ../N64Recomp/RecompiledFuncs/funcs_22.c ../N64Recomp/RecompiledFuncs/funcs_23.c; rg -n -C 6 "jalr|8013D880|0x17C|80086450|80086FC4" ../N64Recomp/RecompiledFuncs/funcs_21.c ../N64Recomp/RecompiledFuncs/funcs_22.c ../N64Recomp/RecompiledFuncs/funcs_23.c ../rogue_squadron64/symbol_files/main_overlay.txt`, then classify every read and edge. No game build or soak is planned.
