# M4 producer/consumer index provenance revisit (s2556)

This is a new angle on the open M4 question: enumerate the complete generated
producer table and the indirect consumer's index source, rather than adding a
second literal-offset census or port probe.

## Discriminator

| Edge | Generated evidence | Result |
|---|---|---|
| Producer entry layout | `funcs_7.c:0x8002642C–0x80026434` stores three halfwords at `DMEM[0xB00+r7]`, `0xB02+r7`, and `0xB04+r7` | Complete |
| Producer slot progression | `0x80026450` increments `r7` by `0x6`; its entry starts at zero in the caller path | Slots are `0x00, 0x06, 0x0C, ...` |
| Producer values | stores are sourced from `v0`, `v1`, and `a0`, each prepared as `0x670`-derived pointers by the surrounding path | 0x670-derived producer confirmed |
| Indirect consumer | `0x80026640–0x8002664C` computes `v0 = v1 & 0x7F`, then loads `B00/B02/B04` at that byte offset | One complete consumer |
| Consumer index source | `0x800265A8` loads `v1` from `MEM_BU(MEM_BU(0,0xC70),0xB74)`; the branch to `0x80026640` requires `(v1 >> 6) == 2` | Runtime byte, not statically bounded |
| Consumer continuation | `0x80026650` feeds the loaded bases into the shared `0x8400139C` path | Consumer is live in the generated control flow |

## Outcome

`H-static-only` is selected. The generated source proves a real indirect
consumer and a real 0x670-derived producer table, but it does not prove that
the runtime byte at the `0xC70`/`0xB74` path has a low-seven-bit value equal to
one of the producer slots in the qualified scene. The missing edge is a
phase-gated runtime join of the consumer index and producer slot; no writer or
legitimacy claim follows from this audit.

The address `0xC70` is DMEM/global-state context in this generated path, not a
retail RDRAM address that the existing oracle can directly observe. Therefore
the next useful experiment, if this thread is resumed, is one batched port
instrument with a positive-control mark, logging producer slot writes and the
consumer index on the same phase gate. No mitigation is authorized.

No generated code, runtime code, or behavior changed.
