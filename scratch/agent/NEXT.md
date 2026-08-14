# NEXT work unit (s939)

HYPOTHESIS-ID: m3-audio-stop-voices-by-handle-contract

Audit the complete `stopVoicesByHandle` idiom at `0x8008DA98` in
`../N64Recomp/RecompiledFuncs/funcs_23.c`, including every generated caller,
handle-to-list-node derivation, list and voice-record accesses, helper edges,
state writes, existing guard coverage, and termination paths. Source-only; do
not add a guard, change game behavior, build, or run a soak.

Competing hypotheses:

- H-stop-voices-by-handle-unclassified: a handle resolves to an invalid list
  node/voice pointer or escapes a terminated list walk.
- H-stop-voices-by-handle-classified: callers and list logic agree on one
  bounded handle/node contract and every termination path is covered.
- H-stop-voices-by-handle-shape-mismatch: callers use distinct handle, node, or
  voice-record contracts that are not translated consistently.

Discriminating measurement: enumerate every reference and caller register
setup, inspect the complete callee and all state/list accesses, derive every
address range and termination path, classify every helper edge, and
cross-check `main_overlay.txt` plus the related `stopVoiceByHandle` contract.
Any handle/node/voice-pointer split, uncovered derived access, or unproven
termination path rejects classification.

Exact command: `rg -n -C 12 "stopVoicesByHandle|8008DA98|8DA98" ../N64Recomp/RecompiledFuncs/funcs_*.c ../rogue_squadron64/symbol_files/main_overlay.txt`, then inspect the complete helper and every caller. No game build or soak is planned.
