# Session 2942 — generated-symbol classification at `0x80099C4C`

| Field | Evidence | Result |
|---|---|---|
| Candidate | `0x80099C4C`, 4 bytes in the project TOML and companion map | Stale placeholder before this iteration |
| Generated body | The generated definition is a fixup `__builtin_trap()` for an invalid decode; no valid callable instructions are present | Invalid-decode gap, not a normal function body |
| Predecessor | `noopHandler_80099C44` starts at `0x80099C44`, size `0x8`, and returns with `jr $ra` at `0x80099C44` | Complete independent stub ends immediately before the candidate |
| Successor | `transformVec3ByAffineMatrix` starts at `0x80099C50`, size `0xAC`, with a normal floating-point transform body | Independent complete routine follows the candidate |
| Companion/m2c evidence | Companion map contained only `fake_func_80099C4C`; no semantic name or source/m2c match exists | No H-CallableSemantic evidence |
| Callers/lookups | Repository search found only symbol-map, definition, header, overlay-registration, and rename-table references; no generated caller or independent lookup | Supports non-callability |
| Callable markers | No prologue, return instruction, or valid standalone body; generated trap confirms invalid decoded bytes | Mechanically non-callable in this bounded evidence |
| Disposition | Renamed to `data_gap_80099C4C` in the project TOML and companion map; generated C/header/overlay metadata and rename helper were already synchronized | H-DataGap selected |

## Competing hypotheses and discriminator

- H-CallableSemantic: rejected; no independent definition, caller, or companion semantic name.
- H-DataGap: selected; the four-byte record is an invalid-decode gap between complete routines with no callable markers or references.
- H-Ambiguous: rejected for this bounded record because the generated body is an explicit invalid-data trap and neither adjacent boundary depends on it as a callable entry.

No runtime experiment or game build was needed; this was a map-only reconciliation.
