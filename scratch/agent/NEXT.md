# NEXT work unit (s943)

Pre-run decision: source-only; do not build, run the game, or enqueue a soak.
The discriminating measurement is a complete callsite and register-indirect
edge inventory for `allocVoiceHandleNode` and the four node `+0xC` copies. A
proven voice-record pointer plus bounded slot-index domain at every reachable
copy selects valid; a non-index or incompatible pointer selects mismatch; an
unresolved edge selects unclassified.

HYPOTHESIS-ID: m3-audio-stop-voices-by-handle-contract

Audit every direct and register-indirect callsite feeding
`allocVoiceHandleNode` and the four sorted handle-list node `+0xC` copies
consumed by `stopVoicesByHandle` at `0x8008DA98`. Separate voice-record
pointers, slot indices, handle values, and channel/fade structures. Cross-check
the companion decomp symbols. No guard, behavior change, build, or soak.

Competing hypotheses:

- H-stop-voices-by-handle-index-valid: every reachable node copy receives a
  bounded 32-slot voice index from a compatible voice-record pointer.
- H-stop-voices-by-handle-index-unclassified: an indirect edge, caller state,
  or pointer/value domain remains unproven.
- H-stop-voices-by-handle-index-mismatch: a reachable edge uses an incompatible
  pointer, handle, state value, or index domain.

Exact command: `rg -n -C 8 "allocVoiceHandleNode|80086450|80086534|80086FC4|8008DA98|0x18\\)|0x64\\(|0xC\\(" ../N64Recomp/RecompiledFuncs/funcs_*.c ../rogue_squadron64/symbol_files/main_overlay.txt`, then classify each callsite and edge. No game build or soak is planned.
