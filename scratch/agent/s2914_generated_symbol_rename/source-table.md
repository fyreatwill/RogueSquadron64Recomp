# Session 2914 bounded symbol table

Interval: `0x80055698..0x800556A0` (end-exclusive).

| Address | Size | Generated body | Companion/source evidence | Callers/lookups | Decision |
|---|---:|---|---|---|---|
| `0x80055698` | 8 | `funcs_12.c` emits `fake_func_80055698` with only `lbu $v1, 0x19($v0)` and `addiu $a0, $v1, 1`; there is no prologue, return, or standalone callable body | Companion map retains `fake_func_80055698`; `initPlayerStructs` ends at `0x80055698` and `loadTxtFile` begins at `0x800556A0`; no companion semantic name exists | Exact searches found only the definition, header, overlay metadata, and map entries; no generated call or address lookup | Rename to `data_gap_80055698` in the companion map, project symbol map, regeneration-safe rename table, and generated C/header/overlay metadata |

The bounded structure, exact adjacent callable boundaries, and absence of an
independent caller prove this is non-callable split/data material rather than a
callable semantic function. The Debug target rebuilt successfully.
