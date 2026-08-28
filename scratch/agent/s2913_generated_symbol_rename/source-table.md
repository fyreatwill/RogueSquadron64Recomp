# Session 2913 bounded symbol table

Interval: `0x800555E8..0x800555F0` (end-exclusive).

| Address | Size | Generated body | Companion/source evidence | Callers/lookups | Decision |
|---|---:|---|---|---|---|
| `0x800555E8` | 8 | `j 0x800555F0`; `nop`; generated host body tail-calls `initPlayerStructs` | Companion `main_overlay.txt` retains `fake_func_800555E8`; the next complete symbol is `initPlayerStructs` at `0x800555F0` | No generated call or address-lookup reference beyond the definition and overlay registration; the body is nevertheless a callable jump veneer | Leave `fake_func_800555E8` unchanged (H-Ambiguous) |

The bounded reconciliation command independently reported `candidate 0x800555E8
fake_func_800555E8: ambiguous-or-fake` and renamed zero references in zero files.
The veneer is not mechanically provable data, while the companion project
provides no semantic name for the callable entry, so neither H-CallableSemantic
nor H-DataGap is selected.
