# Session 2985 candidate table

| Field | Evidence | Result |
|---|---|---|
| Candidate | `0x80023968`, generated size `0x8`, main overlay | bounded target |
| Body | `mul.s f18,f5,f14` at `0x80023968`; `add.s f16,f16,f17` at `0x8002396C` | two-instruction fragment |
| Predecessor | `getLoadedTextureCount` ends at `0x80023968` with its return delay slot at `0x80023964` | complete preceding routine |
| Successor | `emitMaterialRenderModeDL` starts at `0x80023970` with a stack-frame prologue | complete following routine |
| Generated callers | no references other than the declaration and overlay registration | no standalone call contract |
| Companion semantic map | `main_overlay.txt` defined the address as `fake_func_80023968`; no alternate semantic entry exists | no callable identity |
| Independent lookup | no companion m2c/source function or exact semantic name for the two instructions | no rename beyond mechanical classification |

## Decision

`H-boundary-gap` selected. The record is executable-looking but has no
standalone entry contract and is bounded by complete routines, so it is
classified as `data_gap_80023968`. `H-semantic-fragment` and
`H-ambiguous-fragment` are not selected for this candidate.

The regeneration-safe rename script updated the companion-derived generated
function declaration, definition, and overlay registration. No game logic or
runtime behavior changed.
