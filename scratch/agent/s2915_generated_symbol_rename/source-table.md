# Session 2915 bounded symbol table

Interval: `0x80055A2C..0x80055A30` (end-exclusive).

| Address | Size | Generated body | Companion/source evidence | Callers/lookups | Decision |
|---|---:|---|---|---|---|
| `0x80055A2C` | 4 | `funcs_12.c` emits `fake_func_80055A2C` with only `subu $a0, $a0, $v0`; there is no prologue, return, or standalone callable body | Companion `main_overlay.txt` retains `fake_func_80055A2C` and provides no semantic name; `getVoiceTxtStringPtr` ends at `0x80055A2C` and `initVoiceSubtitleSystem` begins at `0x80055A30` | Exact generated references are only the definition, declaration, and overlay registration; zero generated calls; the sole address occurrence is overlay metadata | `ambiguous-or-fake`: leave unchanged because the short fragment could be split/data material or a callable veneer, and no independent source evidence proves either classification |

The one-instruction record is strong negative evidence against an ordinary
callable body, but unlike the previously reconciled gaps it does not prove
non-callability: the instruction is valid and could be a deliberate entry
fragment. The bounded sweep therefore makes no map, generated-file, or
rename-table change.
