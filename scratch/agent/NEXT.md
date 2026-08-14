# NEXT work unit (s937)

HYPOTHESIS-ID: m3-audio-voice-stop-contract

Audit the complete `musyxStopVoice` idiom at `0x80092368` in
`../N64Recomp/RecompiledFuncs/funcs_24.c`, including every generated caller,
the relationship between pointer/index arguments, voice-slot arithmetic,
state writes, existing guard coverage, and sibling callers in the same audio
paths. Source-only; do not add a guard, change game behavior, build, or run a
soak.

Competing hypotheses:

- H-voice-stop-unclassified: a caller supplies an invalid voice index/base,
  or the stop target escapes its intended mixer record.
- H-voice-stop-classified: callers agree on a bounded mixer index and the
  existing guards cover the base/index contract.
- H-voice-stop-shape-mismatch: callers use pointer and index contracts that
  must be translated or are distinct; record the exact split and stop.

Discriminating measurement: enumerate every reference and caller register
setup, inspect the complete callee and all state/slot accesses, derive every
address range and termination path, classify every helper edge, and
cross-check `main_overlay.txt` plus the two caller chains identified in s935.
Any pointer/index split, uncovered derived access, or unproven termination
path rejects classification.

Exact command: `rg -n -C 12 "musyxStopVoice|80092368|92368" ../N64Recomp/RecompiledFuncs/funcs_*.c ../rogue_squadron64/symbol_files/main_overlay.txt`, then inspect the complete helper and every caller. No game build or soak is planned.
