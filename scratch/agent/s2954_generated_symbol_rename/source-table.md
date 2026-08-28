# Generated-symbol sweep: `0x800AA6CC`

Candidate: `0x800AA6CC`, project symbol `fake_func_800AA6CC`, size `0x4`.

## Competing hypotheses and discriminator

| Hypothesis | Predicted evidence | Decision rule |
|---|---|---|
| H-Callable | Standalone prologue/return plus an independent caller or exact companion semantic name | Rename to that semantic name |
| H-Fragment | Valid instructions form a split executable fragment, but no independent entry/caller/name exists | Preserve address identity unless a stronger classification is available |
| H-DataGap | Bytes are mechanically non-callable data or a recompiler false split between complete functions | Rename mechanically to `data_gap_800AA6CC` |

The discriminator is the complete generated span and its exact neighboring
bodies, combined with caller/lookup and companion-map searches.

## Evidence

| Evidence | Result | Implication |
|---|---|---|
| Exact span and boundaries | `buildTransformMatrixFromEulerAngles` ends at `0x800AA6C8` and returns; the candidate is the four-byte word at `0x800AA6CC`; `npcPredictedRangeCheck` begins at `0x800AA6D0` with its normal stack-frame prologue. | The candidate is a short fragment immediately before the established callable body. |
| Generated decode | `funcs_28.c` contains only `lw $v0, 0x24($fp)` in the candidate body, with no stack setup, return, or independent control-flow body. | This is a preamble/entry fragment, not a standalone function. |
| Callers and lookups | The generated-tree search found no call or absolute lookup targeting `0x800AA6CC`; callers target `npcPredictedRangeCheck` at `0x800AA6D0`. | No separate callable identity is needed for dispatch. |
| Companion map | `rogue_squadron64/symbol_files/mission_overlay.txt` preserves `fake_func_800AA6CC` immediately before the named `npcPredictedRangeCheck` entry. | The adjacent semantic name and exact boundary identify the fragment as `npcPredictedRangeCheckPreamble`. |

## Classification

The evidence selects **H-Callable** in the bounded naming sense: this is a
recognized callable-entry preamble fragment with an exact companion semantic
name, not an independent game routine. It is renamed to
`npcPredictedRangeCheckPreamble` in the project map, companion map,
regeneration-safe rename table, and generated declaration/definition/overlay
registration. No gameplay or runtime behavior is changed.
