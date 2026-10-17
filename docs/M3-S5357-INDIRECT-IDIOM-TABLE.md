# M3 s5357 — consolidated indirect-control-flow idiom table

Tool: `tools/audit_indirect_idiom_table.py` (static, over `../N64Recomp/RecompiledFuncs/funcs_*.c`).
Positive control (runs first, same invocation): a clean synthetic jump-table passes and
4/4 injected defects (label outside function, missing `switch_error` default,
non-contiguous cases, unassigned `jr_addend`) are each flagged.

| Class | Sites | Unresolved |
|---|---|---|
| `jr $ra` returns | 2,546 | n/a (not an indirect target) |
| `jr` jump-table switches | 177 (2,278 case arms) | 0: all contiguous 0..n-1, all `goto` labels defined in the same function, all end in `switch_error`, all `jr_addend` assigned |
| `jr/jalr` via `LOOKUP_FUNC(reg)` | remainder of 343 non-ra/non-zero sites | loud-fail through `get_function` (s4821) |
| `jr/jalr $zero` | 114 | all in data-decoded-as-code regions (s4821) |
| lwl/lwr pairs | closed s5347 | 0 |
| branch-likely / delay-slot branch | closed s5346 | 0 |

Table count (177) matches the independent s4821 census. Single-source caveat: the
jump-table check is on generated C, not on the ROM table words; N64Recomp's table
size inference is trusted, and an under-sized table fails loudly via `switch_error`.
Class closed; no new guard needed.
