# Session 2939 — generated-symbol classification at 0x80094348

| Field | Evidence | Result |
|---|---|---|
| Candidate | `0x80094348`, size `0x8` in the project TOML and companion map | Stale placeholder before this iteration |
| Generated body | `funcs_25.c` emits `j L_80094370` at `0x80094348`, followed by `nop` at `0x8009434C`; the recompiler cannot form a standalone body and emits `do_break` | Two-instruction jump fragment, not a normal function body |
| Predecessor | `computeVoiceVolumePanCoefficients` starts at `0x800940D4` with size `0x274`, ending at `0x80094348` | Candidate is immediately after a complete named routine |
| Successor | `startSongSequence` starts at `0x80094350` and its generated body reaches label `L_80094370` | Candidate jumps into the successor's body, not to an independent return |
| Callable shape | No stack/frame prologue, saved return state, or return sequence in the 8-byte record | H-DataGap |
| Companion/m2c semantic name | No companion semantic name; companion entry was `fake_func_80094348` | No H-CallableSemantic evidence |
| Callers/lookups | Repository search found no caller or independent lookup of `fake_func_80094348`, `func_80094348`, or `0x80094348`; live generated references are definition/header/overlay registration only | Supports H-DataGap |
| Invalid filler | The generated function body is a recompiler trap for the unhandled intra-function jump; this is a split/fixup record, not an independently callable implementation | Consistent with H-DataGap |

## Disposition

Classified as H-DataGap and renamed to `data_gap_80094348` in the project
symbol map and companion map. The generated C/header/overlay metadata and
regeneration-safe rename helper already had this name, so no regeneration was
performed.
