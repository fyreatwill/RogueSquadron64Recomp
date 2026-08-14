# NEXT work unit (s938)

HYPOTHESIS-ID: m3-audio-stop-by-key-contract

Audit the complete `stopVoiceByKey` idiom at `0x80086914` in
`../N64Recomp/RecompiledFuncs/funcs_21.c`, including every generated caller,
key-to-voice-index derivation, voice-array accesses, calls into low-level stop
helpers, state writes, existing guard coverage, and termination paths. Source-
only; do not add a guard, change game behavior, build, or run a soak.

Competing hypotheses:

- H-stop-by-key-unclassified: a key resolves to an invalid voice index/base or
  escapes the intended voice record before low-level stop.
- H-stop-by-key-classified: callers and lookup logic agree on a bounded voice
  index and existing guards cover the base/index contract.
- H-stop-by-key-shape-mismatch: callers use distinct key, pointer, or index
  contracts that are not translated consistently.

Discriminating measurement: enumerate every reference and caller register
setup, inspect the complete callee and all state/slot accesses, derive every
address range and termination path, classify every helper edge, and
cross-check `main_overlay.txt` plus the `musyxStopVoice` edge audited in s937.
Any key/pointer/index split, uncovered derived access, or unproven termination
path rejects classification.

Exact command: `rg -n -C 12 "stopVoiceByKey|80086914|86914" ../N64Recomp/RecompiledFuncs/funcs_*.c ../rogue_squadron64/symbol_files/main_overlay.txt`, then inspect the complete helper and every caller. No game build or soak is planned.
