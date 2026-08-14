# NEXT work unit (s942)

Pre-run decision: this iteration will not build or run the game. The
discriminating measurement is an exhaustive generated-source inventory of
node `+0xC` writers/readers, allocator and reuse paths, and list termination,
cross-checked against the companion symbol file. A bounded writer/index,
compatible node layout, and reachable sentinel would select the valid
hypothesis; any incompatible writer/domain or unresolved indirect lifecycle
edge selects unclassified/mismatch.

HYPOTHESIS-ID: m3-audio-stop-voices-by-handle-contract

Audit every generated writer of voice-record `+0x64` and the allocator/index
return paths feeding the sorted handle-list node `+0xC` consumed by
`stopVoicesByHandle` at `0x8008DA98`. Separate handle values, slot indices,
and unrelated structures; require direct register provenance or classify the
path as unproven. Cross-check companion decomp symbols. Source-only; do not
add a guard, change game behavior, build, or run a soak.

Competing hypotheses:

- H-stop-voices-by-handle-index-valid: every `+0x64` value copied into node
  `+0xC` is a bounded 32-slot index, with compatible allocator and reuse paths.
- H-stop-voices-by-handle-index-unclassified: local writers agree, but one or
  more `+0x64` writers, indirect paths, or value domains remain unproven.
- H-stop-voices-by-handle-index-mismatch: a `+0x64` writer or caller uses a
  handle/float/state value, incompatible index domain, or incompatible layout
  on the same record path.

Discriminating measurement: an exhaustive generated-source reference inventory
of all `+0x64` writers/readers in the voice-record functions, their register
provenance and caller contexts, every node `+0xC` copy, allocator return, and
list termination, plus a decomp-symbol cross-check. A proven bounded index at
every copy selects valid; a non-index value selects mismatch; any unresolved
writer or indirect edge selects unclassified.

Exact command: `rg -n -C 8 "0x64\\(|0X64|80086450|80086534|80086FC4|8008DA98|8008DA4C|8013D880|80141AD0|0x17C|0x2780|0x5100|0x50FC" ../N64Recomp/RecompiledFuncs/funcs_*.c ../rogue_squadron64/symbol_files/main_overlay.txt`, then classify each writer and lifecycle edge. No game build or soak is planned.
