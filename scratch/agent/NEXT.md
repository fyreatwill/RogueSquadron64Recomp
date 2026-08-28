# NEXT work unit (s2927) — M4 producer/consumer register-lifetime audit

HYPOTHESIS-ID: m4-accumulator-boundary-revisit

The sweep revisit rule selects the parked M4 boundary. Perform one bounded
static audit of the producer slot register and the indirect consumer's index
register in the checked-in Factor 5 generated source. Do not add probes,
change runtime behavior, or repeat the rejected retail boundary watch.

## Competing hypotheses and discriminator

- H-SharedRegisterState: producer `r7` and consumer `r7`/`r3&0x7f` share a
  task-local state path, so static lifetime proves the equality or its reset.
- H-IndependentState: producer slot and consumer index are independently
  derived; static source cannot prove equality and the dynamic join remains
  open.
- H-ConsumerNeverReaches: the consumer branch has no complete path from the
  resident overlay entry, contradicting the existing positive-control trace.

The discriminator is a complete table of every assignment to producer `r7`
from the producer entry through its B00/B02/B04 stores, every assignment to
consumer `r7`, `r3`, and `r2` before `0x13D8`, all DMEM reset/task boundaries,
and whether the existing s2578 dynamic producer/consumer rows can be explained
by that static path. H-SharedRegisterState requires an explicit shared/reset
edge; H-IndependentState is selected if the paths remain distinct; a missing
consumer path would select H-ConsumerNeverReaches.

## Exact commands

Use the already-qualified ground-truth result (oracle cannot observe RSP DMEM)
and inspect only the bounded generated regions:

```sh
sed -n '4680,5020p' build/factor5_ucode/factor5_ucode_recompiled.c
sed -n '5180,5445p' build/factor5_ucode/factor5_ucode_recompiled.c
rg -n 'r7 =|r3 =|r2 =|0XB00|0XB02|0XB04|0XC70|0XB74|OVL20_13D8' build/factor5_ucode/factor5_ucode_recompiled.c
```

Record the complete table at
`scratch/agent/s2927_m4_register_lifetime/audit.md`. No build or game run is
needed unless the source audit discovers a regeneration mismatch.
