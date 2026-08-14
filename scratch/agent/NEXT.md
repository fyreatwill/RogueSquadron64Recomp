# NEXT work unit (s933)

HYPOTHESIS-ID: m3-audio-adsr-table-class

Audit the complete `musyxSetVoiceAdsrFromTable` idiom at `0x8008A8C4` in
`../N64Recomp/RecompiledFuncs/funcs_22.c`, including every generated caller,
voice-index arithmetic, ADSR-table search bounds, table-entry reads, slot
writes, and helper edges. Source-only; do not add a guard, change game
behavior, build, or run a soak.

Competing hypotheses:

- H-adsr-table-unclassified: a caller or ADSR id supplies an invalid slot,
  table base, or search index, or a derived slot write escapes its intended
  voice record.
- H-adsr-table-classified: callers agree, the table search is bounded by its
  sentinel/count contract, and all slot/table accesses have fixed safe ranges.
- H-adsr-table-shape-mismatch: callers use distinct contracts; record
  the exact split and stop.

Discriminating measurement: enumerate every reference and caller register
setup, inspect the complete callee and all loop/sentinel exits, derive every
table and slot access range, classify every helper edge, and cross-check
`main_overlay.txt`. Any caller split, uncovered derived access, or unproven
termination path rejects classification.

Exact command: `rg -n -C 12 "musyxSetVoiceAdsrFromTable|8008A8C4|8A8C4" ../N64Recomp/RecompiledFuncs/funcs_22.c ../N64Recomp/RecompiledFuncs/funcs_24.c ../N64Recomp/RecompiledFuncs/funcs_26.c ../rogue_squadron64/symbol_files/main_overlay.txt`, then inspect the complete helper and every caller. No game build or soak is planned.
