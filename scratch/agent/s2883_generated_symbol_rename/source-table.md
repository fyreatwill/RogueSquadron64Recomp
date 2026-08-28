# s2883 generated-symbol census

Interval examined: `0x800AF700` through `0x800BAA00` (exclusive).

| Address | Generated record | Classification | Evidence | Action |
|---|---|---|---|---|
| `0x800B2628` | `fake_func_800B2628` | H-Ambiguous / data gap | 8-byte load/store fragment between complete named bodies; companion retains the fake name and provides no semantic candidate. | Unchanged |
| `0x800B42BC` | `fake_func_800B42BC` | H-DataGap | 4-byte fragment immediately before `playerXwingInit` at `0x800B42C0`; companion boundary and existing redefs agree. | `playerXwingInitPreamble` |
| `0x800B47C4` | `fake_func_800B47C4` | H-DataGap | 12-byte setup fragment immediately before `menuControllerInput` at `0x800B47D0`; companion boundary and existing redefs agree. | `menuControllerInputPreamble` |
| `0x800B58B4` | `fake_func_800B58B4` | H-DataGap | 16-byte fragment immediately before `playerAwingInit` at `0x800B58C0`; companion boundary and existing redefs agree. | `playerAwingInitPreamble` |
| `0x800B75C4` | `fake_func_800B75C4` | H-DataGap | 12-byte fragment immediately before `playerYwingInit` at `0x800B75D0`; companion boundary and existing redefs agree. | `playerYwingInitPreamble` |
| `0x800B89F4` | `fake_func_800B89F4` | H-DataGap | Trap-filled 12-byte fragment immediately before `playerVwingInit` at `0x800B8A00`; companion boundary and existing redefs agree. | `playerVwingInitPreamble` |

The bounded reconciliation command renamed 15 references in `funcs_30.c`,
`funcs_31.c`, and the generated symbol tables. No callable body was renamed.
