# NEXT work unit (s947)

Pre-run decision: source-only; do not build, run the game, or enqueue a soak.
The discriminating measurement is an exhaustive `+0x64` writer/value-flow
inventory: sentinel, constructed, or copied composite handles at every writer
select valid; an incompatible writer selects mismatch; an unresolved source or
indirect target selects unclassified.

HYPOTHESIS-ID: m3-audio-stop-voices-by-handle-contract

Audit every remaining generated writer of voice-record handle field `+0x64`.
Classify whether it constructs a composite handle, writes the `-1` sentinel,
copies an already validated handle, or has unresolved provenance. Include
register-indirect audio-overlay edges and companion-symbol names. No guard,
behavior change, build, or soak.

Competing hypotheses:

- H-stop-voices-by-handle-index-valid: all live `+0x64` writers preserve the
  composite-handle/sentinel contract established by note-on and stop paths.
- H-stop-voices-by-handle-index-unclassified: a candidate indirect edge or
  writer remains unresolved.
- H-stop-voices-by-handle-index-mismatch: a reachable writer supplies a
  non-voice record or incompatible handle/state value.

Discriminating measurement: exhaustive `+0x64` store inventory, source/value
flow at each writer, all audio-overlay `jalr` setup, and companion-symbol
cross-check. Sentinel/constructed/copied valid values at every writer select
valid; an incompatible writer selects mismatch; unresolved source or target
selects unclassified.

Exact command: `rg -n -C 8 "0x64|0X64|64\\(" ../N64Recomp/RecompiledFuncs/funcs_21.c ../N64Recomp/RecompiledFuncs/funcs_22.c ../N64Recomp/RecompiledFuncs/funcs_23.c; rg -n -C 6 "jalr|80086450|allocVoiceHandleNode|80086FC4|startNoteOnVoice" ../N64Recomp/RecompiledFuncs ../rogue_squadron64/symbol_files/main_overlay.txt`, then classify every writer and edge. No game build or soak is planned.
