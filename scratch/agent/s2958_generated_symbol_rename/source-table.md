# 0x800AEC54 classification

## Discriminator table

| Hypothesis | Evidence required | Current result |
| --- | --- | --- |
| H-Callable | Standalone prologue/body/return, callable references, and an exact companion semantic name | Refuted: no standalone callable body, no callers, and the companion retains the fake name |
| H-Fragment | Valid executable instructions but callable status remains ambiguous | Refuted: the generated body is an explicit invalid-decode trap rather than executable instructions |
| H-DataGap | Exact bounded interval between neighboring entries, invalid/data decode, and no callable references | Selected: all three conditions are present |

## Source table

| Field | Observation |
| --- | --- |
| Candidate | `fake_func_800AEC54`, menu overlay, VRAM `0x800AEC54`, size `0xC` in `syms/rogue_squadron.syms.toml` |
| Generated span | `0x800AEC54`–`0x800AEC5F` (3 instructions / 12 bytes); `initCraftSelectScreen` begins exactly at `0x800AEC60` |
| Generated body | `../N64Recomp/RecompiledFuncs/funcs_29.c` emits `fake_func_800AEC54` as `__builtin_trap()` with the explicit gap-filler note; it has no prologue, return, or game logic |
| Previous real body | `static_6_800AEC48` occupies the preceding bytes and its complete body continues beyond the candidate; no return boundary identifies a callable entry at `0x800AEC54` |
| Next real body | `initCraftSelectScreen` has the normal stack-frame prologue at `0x800AEC60` and a 0x760-byte overlay record |
| Companion map | `../rogue_squadron64/symbol_files/menu_overlay.txt` lists `fake_func_800AEC54` and gives no semantic replacement; the adjacent `initCraftSelectScreen` entry is independent |
| Callers / lookups | Exact-reference search found only the declaration, trap definition, overlay registration, source-map entries, and diagnostic address comments/stores; no generated call or independent absolute lookup targets the candidate |
| Existing rename table | `tools/rename_generated_symbols.py` already maps `fake_func_800AEC54` to `data_gap_800AEC54`, so the rename is regeneration-safe |

## Decision

Rename the mechanical placeholder to `data_gap_800AEC54` in the companion
map, project symbol map, and generated artifacts. This is a naming change only;
the bytes remain non-callable and the generated trap remains unchanged.
