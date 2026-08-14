# NEXT work unit (s944)

Pre-run decision: source-only; do not build, run the game, or enqueue a soak.
The discriminating measurement is a complete caller/return/value-flow inventory
for `startNoteOnVoice` and the voice-record `+0x64` writers feeding the four
sorted-node `+0xC` copies. A bounded returned slot plus a proven record pointer
selects valid; an incompatible value selects mismatch; an unresolved edge
selects unclassified.

HYPOTHESIS-ID: m3-audio-stop-voices-by-handle-contract

Audit every direct and register-indirect caller of `startNoteOnVoice`, trace
its returned slot/index into the voice table and `+0x64` handle field, and
connect each record to the four sorted handle-list node `+0xC` copies consumed
by `stopVoicesByHandle` at `0x8008DA98`. Separate voice-record pointers, slot
indices, handle values, and channel/fade structures. Cross-check companion
decomp symbols. No guard, behavior change, build, or soak.

Competing hypotheses:

- H-stop-voices-by-handle-index-valid: every reachable node copy receives a
  bounded 32-slot voice index from a compatible voice-record pointer.
- H-stop-voices-by-handle-index-unclassified: an indirect edge, caller state,
  or pointer/value domain remains unproven.
- H-stop-voices-by-handle-index-mismatch: a reachable edge uses an incompatible
  pointer, handle, state value, or index domain.

Exact command: `rg -n -C 8 "startNoteOnVoice|80086FC4|0x64\\(|0x18\\)|0xC\\(" ../N64Recomp/RecompiledFuncs/funcs_*.c ../rogue_squadron64/symbol_files/main_overlay.txt`, then classify each caller and value-flow edge. No game build or soak is planned.
