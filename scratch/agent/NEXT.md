# NEXT work unit (s930)

HYPOTHESIS-ID: m3-audio-compand-class

Audit the complete `audioCompandS16` idiom at `0x8009DD7C`, including every
generated caller and every interior target entering its sign/region paths.
Source-only; do not add a guard, change game behavior, build, or run a soak.

Competing hypotheses:

- H-compand-unclassified: an entry path reaches the helper with an invalid
  sign/region contract or an unsafe indirect edge.
- H-compand-classified: all entries and callers use fixed arithmetic contracts,
  with bounded region selection, clamp, sign restoration, and termination.
- H-compand-shape-mismatch: one caller or interior entry uses a distinct
  contract; record the exact split and stop.

Discriminating measurement: enumerate every `audioCompandS16` reference,
caller register setup, target address, sign/region branches, arithmetic bounds,
and return path; cross-check `main_overlay.txt` and the complete generated
helper. Any data-derived target, omitted clamp/sign path, unsafe arithmetic
bound, or caller/entry shape split rejects classification.

Exact commands: `rg -n -C 8 "audioCompandS16|8009DD7C|DD7C" ../N64Recomp/RecompiledFuncs/funcs_27.c ../rogue_squadron64/symbol_files/main_overlay.txt`, then inspect the complete helper and every reference. No game build or soak is planned.
