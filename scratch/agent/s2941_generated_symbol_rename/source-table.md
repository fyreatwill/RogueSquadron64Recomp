# Session 2941 — generated-symbol classification at `0x80097D58`

| Field | Evidence | Result |
|---|---|---|
| Candidate | `0x80097D58`, 8 bytes in the project TOML and companion map | Stale placeholder before this iteration |
| Generated body | `lw $fp,0x88($sp)` at `0x80097D58`; `addiu $sp,$sp,0x90` at `0x80097D5C`; no `jr $ra` | Isolated epilogue/fixup fragment, not a normal function body |
| Predecessor | `playSongById` starts at `0x80097C2C`, size `0x12C`, and has its own `jr $ra` at `0x80097D40` with delay-slot completion at `0x80097D54` | Candidate follows a complete independent routine |
| Successor | `clearStreamedVoiceFlags` starts at `0x80097D60`, size `0x48`, with a fresh stack decrement at `0x80097D68` | Independent complete routine follows candidate |
| Companion/m2c evidence | Companion map contained only `fake_func_80097D58`; no semantic name or source/m2c match exists | No H-CallableSemantic evidence |
| Callers/lookups | Repository search found only definition/header/overlay registration and symbol-map entries; no generated caller or independent address lookup | Supports non-callability |
| Callable markers | No standalone prologue, return instruction, or complete body; the two instructions only restore frame state | Mechanically non-callable in this bounded evidence |
| Disposition | Renamed to `data_gap_80097D58` in the project map, companion map, generated C/header/overlay metadata, and regeneration-safe rename table | H-DataGap selected |

## Competing hypotheses and discriminator

- H-CallableSemantic: rejected; no independent definition, caller, or companion semantic name.
- H-DataGap: selected; the record is an isolated two-instruction epilogue between complete routines, with no callable markers or references.
- H-Ambiguous: rejected for this bounded record because its predecessor already returns and the record has no standalone entry/return shape.

No runtime experiment or game build was needed.
