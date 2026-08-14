# NEXT work unit (s945)

Pre-run decision: source-only; do not build, run the game, or enqueue a soak.
The discriminating measurement is a complete pointer-flow inventory for the
four sorted-node `+0xC` copy sites. Four proven voice-record pointers select
valid; a channel/fade pointer selects mismatch; an unresolved edge selects
unclassified.

HYPOTHESIS-ID: m3-audio-stop-voices-by-handle-contract

Audit the voice-record pointer provenance at `0x80086524`, `0x80086E40`,
`0x8008738C`, and `0x800877E0`, including inline callers and register-indirect
edges. Separate voice-record pointers, slot indices, composite handles, and
channel/fade structures. Cross-check companion decomp symbols. No guard,
behavior change, build, or soak.

Competing hypotheses:

- H-stop-voices-by-handle-index-valid: every reachable node copy receives
  `+0x64` from a live voice-record pointer with a compatible low-byte slot.
- H-stop-voices-by-handle-index-unclassified: an indirect edge, caller state,
  or pointer/value domain remains unproven.
- H-stop-voices-by-handle-index-mismatch: a reachable edge uses a channel/fade
  pointer or incompatible handle/state value.

Discriminating measurement: inventory each copy site's base-register
derivation, slot arithmetic, caller boundary, and register-indirect edge, then
cross-check companion symbols. Four proven voice-record pointers select valid;
a non-voice pointer selects mismatch; an unresolved edge selects unclassified.

Exact command: `rg -n -C 8 "80086524|80086E40|8008738C|800877E0|0x17C|-0x2780|jalr" ../N64Recomp/RecompiledFuncs/funcs_21.c ../N64Recomp/RecompiledFuncs/funcs_22.c ../N64Recomp/RecompiledFuncs/funcs_23.c ../rogue_squadron64/symbol_files/main_overlay.txt`, then classify each copy-site pointer flow. No game build or soak is planned.
