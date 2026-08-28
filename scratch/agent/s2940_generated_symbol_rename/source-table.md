# Session 2940 — generated-symbol classification at 0x8009711C

| Field | Evidence | Result |
|---|---|---|
| Candidate | `0x8009711C`, size `0x4` in the project TOML and companion map | Stale placeholder before this iteration |
| Generated body | `funcs_25.c` emits only `j L_8009713C` at `0x8009711C`; the recompiler emits `do_break` because the target is not a standalone body | Four-byte jump fragment, not a normal function body |
| Predecessor | `initSongSequencerPools` starts at `0x80097088` with size `0x94`, ending at `0x8009711C` | Candidate is immediately after a complete named routine |
| Successor/boundary | `resetSongSubsystemCounter` starts at `0x80097120`; the jump target `0x8009713C` is inside `bindMacroIdsToSoundGroup`, which starts at `0x80097130` | Candidate transfers into a later routine rather than to an independent return |
| Callable shape | No stack/frame prologue, saved return state, or return sequence in the record | H-DataGap |
| Companion/m2c semantic name | Companion entry was `fake_func_8009711C`; no semantic companion name exists | No H-CallableSemantic evidence |
| Callers/lookups | Repository search found no caller or independent lookup of `fake_func_8009711C`, `func_8009711C`, or `0x8009711C`; live generated references are definition/header/overlay registration only | Supports H-DataGap |
| Invalid filler | The generated body is a recompiler trap for an intra-region jump fragment, not an independently callable implementation | Consistent with H-DataGap |

## Disposition

Classified as H-DataGap and renamed to `data_gap_8009711C` in the project
symbol map and companion map. The generated C/header/overlay metadata and
regeneration-safe rename helper already had this name, so no regeneration was
performed.
