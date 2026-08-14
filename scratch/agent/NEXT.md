# NEXT work unit (s941)

HYPOTHESIS-ID: m3-audio-stop-voices-by-handle-contract

Audit the sorted handle-list node `+0xC` index contract consumed by
`stopVoicesByHandle` at `0x8008DA98`: enumerate every generated writer,
initializer, allocator, unlink/reuse path, and sentinel that can establish or
invalidate the slot index, then cross-check companion decomp symbols. Source-
only; do not add a guard, change game behavior, build, or run a soak.

Competing hypotheses:

- H-stop-voices-by-handle-index-valid: every node `+0xC` writer derives an
  index from the bounded 32-slot allocator and preserves the handle-list
  contract through unlink/reuse.
- H-stop-voices-by-handle-index-unclassified: local writers agree, but a
  writer, indirect path, or lifecycle edge leaves range/value legitimacy open.
- H-stop-voices-by-handle-index-mismatch: writers use incompatible index
  domains, sentinels, or node layouts.

Discriminating measurement: an exhaustive generated-source reference inventory
for node `+0xC`, its writers, allocator return values, and list termination,
plus a decomp-symbol cross-check. Any writer that can produce an out-of-range
index or incompatible node contract selects unclassified/mismatch; otherwise
the index lifecycle is classified.

Exact command: `rg -n -C 8 "0xC\(|0XC,|0xC\)|0XC\)|80086534|allocVoiceHandleNode|resolveVoiceSlotByHandle|0x5100|0x8013AE00" ../N64Recomp/RecompiledFuncs/funcs_*.c ../rogue_squadron64/symbol_files/main_overlay.txt`, then classify each writer and lifecycle edge. No game build or soak is planned.
