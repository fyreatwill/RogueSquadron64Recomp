# Session 2917 source table — `0x80059B4C..0x80059B50`

| Address | Size | Generated body | Companion/source evidence | Callers/lookups | Action |
|---|---:|---|---|---|---|
| `0x80059B4C` | 4 | `sw $fp, 0x48($sp)`; generated as `fake_func_80059B4C` | Immediately precedes the complete `mat34CrossRowsAndCopyPos` body at `0x80059B50`; no semantic companion name or source/m2c address hit | No generated caller or independent address lookup; only the definition and overlay registration | `ambiguous-or-fake`; preserve placeholder |

The isolated instruction is a valid frame-pointer store and therefore does
not mechanically prove a data gap: it could be a split callable fragment.
The bounded reconciliation command returned `renamed 0 references in 0
files` and classified the candidate `ambiguous-or-fake`. No symbol map,
generated file, or rename-table entry changed.
