# Session 2938 — `0x80093E74` classification

| Field | Evidence | Result |
|---|---|---|
| Candidate | `0x80093E74`, 12 bytes, main overlay | Defined short record |
| Generated body | `lw $ra,0x24($sp)`; `lw $fp,0x20($sp)`; `addiu $sp,$sp,0x28`; no `jr $ra` | Isolated epilogue/fixup fragment, not a complete callable body |
| Predecessor | `sqrtf_recomp` at `0x80093E6C`, size `0x8`; `jr $ra` with `sqrt.s` delay slot | Complete named routine ends at candidate |
| Successor | `musyxComputeNotePlaybackRate` at `0x80093E80`, size `0x98`; starts with stack setup | Independent complete named routine follows candidate |
| Companion semantic name | Companion map had only `fake_func_80093E74`; no source-backed name | No semantic callable rename available |
| Generated callers | Search found only the generated definition, header, overlay registration, and rename-table entry | No caller evidence |
| Independent lookups | Search found no address lookup beyond symbol/map surfaces | None |
| Callable markers | No standalone prologue, return instruction, or complete body; only an epilogue fragment | Mechanically non-callable in this bounded evidence |
| Regeneration-safe surfaces | Generated C/header/overlay metadata and rename helper already used `data_gap_80093E74`; project TOML and companion map were stale | Synchronized all map surfaces |

## Decision

H-DataGap selected. The record was renamed to `data_gap_80093E74` in the
project symbol TOML and companion map; generated surfaces were already
synchronized. No runtime experiment or build was needed.
