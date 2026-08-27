# M4 indirect vertex-base alias audit (s2536)

This audit follows the M4 revisit requirement after the generated-symbol
sweep consumed the 15-title revisit window. It tests the previously unexamined
`L_13D8` path, where overlay 0x20 loads vertex bases from DMEM `0xB00/B02/B04`
before calling `L_17F0`.

## Discriminator

| Overlay | B00/B02/B04 reader | L_17F0 pointer loads | 0x670-related provenance |
|---|---|---|---|
| 0x04 | none found | `+0x24`, `+0x1A`, `+0x18/+0x1C` through r11/r12/r13 | direct normal-path bases only |
| 0x10 | none found | same | direct normal-path bases only |
| 0x12 | none found | same | direct normal-path bases only |
| 0x14 | none found | same | direct normal-path bases only |
| 0x18 | none found | same | direct normal-path bases only |
| 0x1C | writes B00/B02/B04; base `r8=0x670` | same shared L_17F0 shape | writes pointers `0x670 + {0x0,0x50,0x78,0xA0,0xC8,0xF0,0x140,0x168,0x190,0x230,0x258,0x2F8,0x320,0x3C0}` into the table |
| 0x20 | loads B00/B02/B04 at `L_13D8` | `+0x24`, `+0x1A`, `+0x18/+0x1C` through loaded r11/r12/r13 | consumes the table written by 0x1C when the shared DMEM state persists |
| 0x24 | none found | same | direct normal-path bases only |

The generated 0x1c writer stores the three pointer values at table offsets
`B00/B02/B04 + r7`, then advances `r7` by six bytes. The 0x20 reader selects
an entry using `(r3 & 0x7f)` and loads those three values. In the normal
direct path, 0x20 instead constructs r11/r12/r13 from `0x670`; both paths
therefore feed the same `L_17F0` loads.

The static ucode-data image at the initial B00 table contains values whose
12-bit addresses include `0x611` and `0x6B6`, but that image is not the
authoritative runtime state: overlay 0x1c has explicit runtime writers for
the table, including pointers derived from `0x670`.

## Result

`H-indirect-consumer` is selected at the static dataflow/provenance scope.
The earlier literal-offset audit was incomplete: the table writer in overlay
0x1c creates 0x670-derived vertex bases, and overlay 0x20's indirect path can
feed them to `L_17F0`, whose loads include the stored `v6` fields. This is a
consumer-path explanation, not proof that a particular table index was live
in the qualified port scene; that dynamic index join remains unmeasured.

No runtime field, mitigation, or generated file changed. No oracle run was
needed because this work unit audited the port's complete static producer /
table-reader / consumer path and did not interpret a retail null.
