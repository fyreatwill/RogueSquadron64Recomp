# NEXT work unit (s934)

HYPOTHESIS-ID: m3-audio-adsr-store-class

Audit the complete `musyxStoreVoiceAdsrParams` idiom at `0x800922C4` in
`../N64Recomp/RecompiledFuncs/funcs_24.c`, including every generated caller,
voice-index arithmetic, voice-array base derivation, ADSR-record reads, slot
writes, existing guard coverage, and helper edges. Source-only; do not add a
guard, change game behavior, build, or run a soak.

Competing hypotheses:

- H-adsr-store-unclassified: a caller supplies an invalid voice index, base,
  or ADSR record pointer, or the derived slot write can escape its intended
  0x88-byte voice record.
- H-adsr-store-classified: callers agree, the existing base guard covers the
  array entry, and the index/record accesses have fixed safe ranges.
- H-adsr-store-shape-mismatch: callers use distinct index or record contracts;
  record the exact split and stop.

Discriminating measurement: enumerate every reference and caller register
setup, inspect the complete callee, derive the exact `index*0x88` range and all
record/slot accesses, classify the base guard and helper edges, and cross-check
`main_overlay.txt`. Any caller split, unbounded index, uncovered base path, or
out-of-record access rejects classification.

Exact command: `rg -n -C 12 "musyxStoreVoiceAdsrParams|800922C4|922C4" ../N64Recomp/RecompiledFuncs/funcs_*.c ../rogue_squadron64/symbol_files/main_overlay.txt`, then inspect the complete helper and every caller. No game build or soak is planned.
