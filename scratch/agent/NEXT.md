# NEXT work unit (s929)

HYPOTHESIS-ID: m3-audio-mix-stereo-class

Audit the complete `audioMixStereoBlock8` idiom at `0x8009DC98`, including
every generated caller, its caller-derived `$t3` indirect targets, both
voice-buffer ranges, all eight sample steps, and target-helper contracts.
Source-only; do not add a guard, change game behavior, build, or run a soak.

Competing hypotheses:

- H-stereo-unclassified: a caller supplies a data-derived or invalid indirect
  target, an unbounded sample range, or a mismatched voice-buffer shape.
- H-stereo-classified: all callers use the same fixed eight-pair contract,
  the return-address-derived targets are fixed and valid, and all local
  accesses terminate within bounded ranges.
- H-stereo-shape-mismatch: one caller uses a distinct buffer/target contract;
  record the exact split and stop.

Discriminating measurement: enumerate every generated caller's `$a0` setup,
the `$t3` origin and resolved target at each call, all eight source/destination
halfword offsets, and loop/termination conditions; cross-check
`main_overlay.txt` and all four target helper bodies. Any omitted access,
unsafe bound, unbounded loop, invalid target, or shape split rejects
classification.

Exact commands: inspect `../N64Recomp/RecompiledFuncs/funcs_27.c` around
`0x8009DC98`, `rg` every `audioMixStereoBlock8` reference and its `$t3`
setup, then inspect the matching `../rogue_squadron64/symbol_files/main_overlay.txt`
entries and all four target helper bodies. No game build or soak is planned.
