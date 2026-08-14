# NEXT work unit (s935)

HYPOTHESIS-ID: m3-audio-voice-attack-class

Audit the complete `musyxTriggerVoiceAttack` idiom at `0x8009231C` in
`../N64Recomp/RecompiledFuncs/funcs_24.c`, including every generated caller,
voice-index arithmetic, voice-slot accesses, state transitions, existing
guard coverage, and helper edges. Source-only; do not add a guard, change
game behavior, build, or run a soak.

Competing hypotheses:

- H-voice-attack-unclassified: a caller supplies an invalid voice index/base,
  or a derived slot access escapes its intended 0x88 voice record.
- H-voice-attack-classified: callers agree, the existing guards cover the
  base/index contract, and all state/slot accesses have fixed safe ranges.
- H-voice-attack-shape-mismatch: callers use distinct contracts; record the
  exact split and stop.

Discriminating measurement: enumerate every reference and caller register
setup, inspect the complete callee and all state/slot accesses, derive every
address range and termination path, classify every helper edge, and
cross-check `main_overlay.txt`. Any caller split, uncovered derived access,
or unproven termination path rejects classification.

Exact command: `rg -n -C 12 "musyxTriggerVoiceAttack|8009231C|9231C" ../N64Recomp/RecompiledFuncs/funcs_*.c ../rogue_squadron64/symbol_files/main_overlay.txt`, then inspect the complete helper and every caller. No game build or soak is planned.
