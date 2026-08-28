# Session 2952 generated-symbol source table

Candidate: `0x8009D8BC`, project symbol `func_8009D8BC`, size `0x8`.

| Check | Evidence | Result |
|---|---|---|
| Exact generated span | `RecompiledFuncs/funcs_27.c` represents `0x8009D8BC..0x8009D8C3` as label `L_8009D8BC` inside `filterVoiceSampleBlock`: `lwc1 $f23,-0x1C19($fp)` followed by unsupported `scd $s3,-0xA09($t7)`. | Two-instruction fragment; no standalone body. |
| Boundaries | `filterVoiceSampleBlock` returns at `0x8009D7C4..0x8009D7C8`; its unusual `bltzal $zero,L_8009D8BC` at `0x8009D7E0` is always false. `applyVoiceDelayFilter` begins at `0x8009D8C4`. | No callable prologue or return at the candidate. |
| Generated callers | The only reference is the internal `static_3_8009D8BC` emitted for the dead branch target from `filterVoiceSampleBlock`; no independent `jal`, lookup, or direct call targets the address. | Not independently callable. |
| Companion map/source | `rogue_squadron64/symbol_files/main_overlay.txt` has no entry for `0x8009D8BC`; it maps `filterVoiceSampleBlock` at `0x8009D7D0` and `applyVoiceDelayFilter` at `0x8009D8C4`. No companion C/m2c semantic name was found. | No human rename is available. |
| Independent lookup/return | Repository search found no independent address lookup or return boundary for the candidate. | Callable rename is not defensible. |

## Classification

The complete comparison selects **H-Fragment**. `0x8009D8BC` is a valid
instruction fragment emitted as a dead internal branch target, not a
standalone callable and not a mechanically bounded data gap. Preserve
`func_8009D8BC` unchanged in the project map, generated files, overlay
registration, and rename helper. No build is authorized by this result.

This is static, single-source evidence about generated/companion boundaries;
it does not establish runtime reachability.
