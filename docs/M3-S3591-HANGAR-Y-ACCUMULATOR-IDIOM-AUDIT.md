# M3 hangar `0x8000` Y/accumulator idiom audit

Session 3591 performed the complete static census requested by `NEXT.md`.
The relevant generated code is the Factor 5 ucode family under
`build/factor5_ucode/`, rather than the ordinary `RecompiledFuncs/funcs_*.c`
tree. The eight sibling overlays (`ovl4`, `ovl10`, `ovl12`, `ovl14`, `ovl18`,
`ovl1c`, `ovl20`, and `ovl24`) share the same producer/consumer layout. The
main generated ucode file shares it too; the `_b` file has no corresponding
vertex-record path.

| Site | Kind | Contract |
|---|---|---|
| `ori r9, r0, 0x670` before `L_162C` | base | DMEM vertex-record table |
| `L_162C` through `L_1740` | writer loop | one record at `r9`, then `r9 += 0x50` |
| `sdv v6[0], 0x18(r9)` at `L_1740` | Y/XY writer | writes computed XY at record `+0x18..+0x1f` |
| `ssv v7[4], 0x1e(r9)` | overlap | overwrites only the final halfword; live `v6` bytes are `+0x18..+0x1d` |
| `sdv v6[8], 0x40(r9)` | paired writer | same field for the second vertex at `base + 0x28` |
| `L_17F0` `llv 0x18(r11/r12/r13)` | consumer | reads the three sorted vertex XY fields |
| `L_17F0` `lh 0x1a(r11/r12/r13)` | Y consumer | reads Y for sorting and RDP YL/YM/YH |
| `L_17F0` `lsv 0x1c(r11/r12/r13)` | consumer | reads the remaining `v6` halfword |
| `L_17F0` stores to `r16+0x02/+0x04/+0x06` | output writer | emits sorted YL/YM/YH to the RDP triangle command |
| `L_17F0` stores to `r16+0x08/+0x0a` | output writer | scales X from record `+0x18` into XL |
| `L_112C` | flush consumer | sends `r16 - 0xd60` bytes from the `0xd60` command buffer |

The `+0x24` clip flags are loaded first at `L_17F0`: all-out flags branch
before any Y/XY read, partial clipping takes its clipping path, and only
zero combined flags reach normal restaging. There is no separate numeric Y
range check; the contract is the producer record and clip flags. The loop's
existing task-controlled condition guards its fixed `0x50` stride. Other
stores at `+0x46`, `+0x48`, `+0x4a`, and `+0x4c` are unrelated record state.

No generated file contains a writer that stores a literal `0x8000` into the
vertex Y field. A `0x8000` value is therefore an input to the `v6`
calculation or a pre-existing record value, not a static writer constant.
The only common-path `+0x1a` loads are the three `L_17F0` Y reads; the extra
`ovl10`/`ovl12` `+0x1a` loads from `r17` are outside this vertex path.

## Verdict

**H-HangarYBounded selected structurally.** All relevant generated overlays
share the `0x670` base, `0x50` record stride, `L_1740` writer, `L_17F0`
consumer, clip gate, and `L_112C` output boundary. No concrete invalid
writer/value was found, so no guard or runtime change is justified. Runtime
allocator/input legitimacy and the unavailable live hangar capture remain
unproven; this is not proof that every observed `0x8000` is legitimate.

Independent evidence lines are (1) the generated `ovl20` instruction path,
including producer, overlap, sort, and RDP stores, and (2) the same site
signature across all eight sibling overlays and the main generated ucode.
