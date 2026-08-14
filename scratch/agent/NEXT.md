# NEXT work unit (s932)

HYPOTHESIS-ID: m3-audio-voice-init-class

Audit the complete `musyxInitVoiceFromSample` idiom at `0x80092128` in
`../N64Recomp/RecompiledFuncs/funcs_24.c`, including both generated callers,
the existing base-pointer guard, slot-index arithmetic, sample-descriptor
reads, all writes, and helper edges. Source-only; do not add a guard, change
game behavior, build, or run a soak.

Competing hypotheses:

- H-voice-init-unclassified: a caller or descriptor supplies an invalid voice
  index/base or data-derived pointer, or the existing guard does not cover the
  full slot access shape.
- H-voice-init-classified: callers agree, the slot calculation is bounded by
  the intended voice table, and all descriptor/slot accesses and helper calls
  have fixed safe contracts.
- H-voice-init-shape-mismatch: the two callers use distinct contracts; record
  the exact split and stop.

Discriminating measurement: enumerate every reference and caller register
setup, inspect the complete callee and existing guard coverage, derive every
slot range from the index/stride, classify every descriptor read and slot
write, and cross-check `main_overlay.txt`. Any caller split, uncovered access,
or data-derived unsafe edge rejects classification.

Exact commands: `rg -n -C 10 "musyxInitVoiceFromSample|80092128|92128" ../N64Recomp/RecompiledFuncs/funcs_22.c ../N64Recomp/RecompiledFuncs/funcs_24.c ../N64Recomp/RecompiledFuncs/funcs_26.c ../rogue_squadron64/symbol_files/main_overlay.txt`, then inspect the complete helper and both callers. No game build or soak is planned.
