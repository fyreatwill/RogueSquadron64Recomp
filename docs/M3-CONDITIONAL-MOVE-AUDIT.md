# M3 conditional-move idiom audit

Session 5561 audited every generated `movz` and `movn` comment in the current
`RecompiledFuncs` tree with `tools/audit_conditional_move.py`.

The census accepts direct and `.word` instruction comments, extracts the MIPS
destination/source/condition registers, and checks the following generated C
guard and assignment. Writes to `$zero` are classified as discarded. The run
included an ordinary nonzero-destination control (`0x800A3914`) and an
invalid/data-gap control (`0x8009F020`).

| measure | result |
|---|---:|
| generated files / functions | 51 / 2,502 |
| instruction occurrences / unique guest PCs | 179 / 149 |
| `movz` / `movn` occurrences | 95 / 84 |
| exact generated translations | 115 |
| `$zero`-destination discards | 64 |
| condition mismatches | 0 |
| assignment mismatches | 0 |
| missing translations | 0 |

The ordinary control translated exactly. The invalid/data-gap control was
classified as an intentional `$zero`-destination discard. No reachable
ordinary conditional-move mismatch was found, so no mitigation is authorized.
This is a static generated-tree result; it does not establish runtime
reachability for data-like sites.
