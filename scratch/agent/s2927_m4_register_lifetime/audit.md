# s2927 M4 producer/consumer register-lifetime audit

## Ground-truth preflight

The retail oracle cannot observe RSP DMEM or `ACCH:ACCM:ACCL`. Its existing
whole-RDRAM control and title/hangar route qualification therefore remain the
independent control, but no new oracle watch can answer this DMEM question.
This unit uses the checked-in generated Factor 5 source and the prior dynamic
producer/consumer trace as two separate evidence lines.

## Discriminator table

| Edge | Source evidence | Result |
|---|---|---|
| Producer entry | `OVL1C_1DDC` assigns `r7 = 0`; the loop at `OVL1C_1E2C` increments `r7` by `1` for object traversal, then returns to `OVL1C_1DDC` for the next outer item | Producer starts from a local zero and does not inherit a consumer index |
| Producer table store | `OVL1C_1ED4` stores `r2/r3/r4` to `B00/B02/B04 + r7`, then `OVL1C_1F04` advances `r7 += 6` | Producer slots are byte offsets `0x00, 0x06, 0x0C, ...` |
| Consumer setup | `OVL20_1320` computes consumer `r7 = r10*40`, then reads `r8 = DMEM[0xC70]` and `r3 = DMEM[0xB74 + r8]` | Consumer `r7` is an object/vertex offset, not the producer table slot; the index source is a runtime DMEM byte |
| Consumer branch | `OVL20_133C` derives `r4 = r3 >> 6`; only `r4 == 2` reaches `OVL20_13D8` | Branch reachability depends on `B74` state, not producer `r7` |
| Indirect lookup | `OVL20_13D8` derives `r2 = r3 & 0x7F` and loads `B00/B02/B04 + r2` | Consumer index is independently derived and need not equal a producer slot |
| Task/overlay boundary | Producer code is in resident overlay `0x1C`; the consumer is in resident overlay `0x20`. No generated assignment transfers producer `r7` into consumer `r3` or `B74` | No static shared-register or assignment edge proves equality |
| Existing dynamic control | s2578 recorded the producer at slot `0x00` and consumer at index `0x00` in the same qualified route, with the route positive control firing | The live join is real, but one observed equal pair does not prove the source of equality |

## Verdict

This selects `H-IndependentState`: the producer slot and consumer index have
distinct derivations and no static equality/reset edge. It rules out
`H-SharedRegisterState` as a register-lifetime explanation. The existing
dynamic row rules out `H-ConsumerNeverReaches`, but the reason the runtime
`B74` value selects a populated producer slot remains unresolved.

The next useful work is not another symbol sweep or a broad retail watch. A
single batched port probe must join the `B74` writer/value to the producer slot
and consumer index on the same phase/task key, with the existing route positive
control. No mitigation, table rewrite, or accumulator change is authorized.

ORIGIN: diagnostic-only static audit. No runtime, generated function,
submodule, or mitigation-shaped behavior changed.
