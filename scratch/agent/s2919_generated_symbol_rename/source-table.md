# Session 2919 source table — `0x8005C61C..0x8005C620`

| Address | Size | Generated body | Companion/source evidence | Callers/lookups | Action |
|---|---:|---|---|---|---|
| `0x8005C61C` | 4 | `addu $v1, $v1, $a0`; the generated snapshot already calls it `checkTrackedNpcProximityForCuePreamble` | The companion map explicitly retains `fake_func_8005C61C`; no companion source or m2c symbol provides the preamble name. It follows the complete `allocAllInitialNpcSlots` return sequence and precedes the complete `checkTrackedNpcProximityForCue` prologue. | Exact searches found only the companion/project placeholder entries and the generated definition, declaration, and overlay registration under the already-applied preamble alias; no generated caller or independent address lookup | `ambiguous-or-fake`; preserve the companion/project placeholder and do not add a new rename |

The one-instruction record is valid executable MIPS, so its lack of a
standalone prologue or return does not prove that it is a data gap. The bounded
reconciliation command returned `renamed 0 references in 0 files` and
classified the companion candidate `ambiguous-or-fake`. No generated file,
symbol map, companion map, or rename-table entry changed.
