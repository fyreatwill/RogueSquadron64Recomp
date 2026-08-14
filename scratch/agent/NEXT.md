# NEXT work unit (s1103)

HYPOTHESIS-ID: submit-producer-boundary

Perform one bounded runtime-free call-chain audit for the two now-proven
generated queue producers: trace the callers and loop/re-entry conditions of
`spTaskSchedulerThread`'s send to `0x8011A818` and
`dpInterruptHandlerThread`'s send to `0x8011A7E8`, and compare them with the
two blocking consumer entry paths. Do not change queue behavior or build.

Competing hypotheses:

* H-producer-reachable: each direct send is reachable from its corresponding
  scheduler/interrupt loop before the blocking wait can persist.
* H-producer-gated: one or both sends are behind a state/flag branch that can
  leave the consumer blocked despite the static producer.
* H-producer-loop-mismatch: producer and consumer are in separate lifecycle
  loops, so the direct sends do not service the observed waits.

Discriminator: for each queue, produce a bounded call/branch table from its
producer entry to the send and from the consumer entry to its blocking recv.
An unconditional or positively dominated producer path in the same active
loop selects H-producer-reachable; a flag/branch that can skip the send selects
H-producer-gated; distinct lifecycle ownership with no common activation path
selects H-producer-loop-mismatch. Computed calls must name their exact target
boundary rather than infer reachability.

Exact commands:

```sh
rg -n -C 8 "spTaskSchedulerThread|dpInterruptHandlerThread|waitForPostSwapAck|osRecvMesg_recomp|0x80019F1C|0x8001C3D8|0x8000C0B4|0x8000C2B8" /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs docs/game-architecture.md
rg -n -C 5 "jal.*spTaskSchedulerThread|jal.*dpInterruptHandlerThread|func_80019F|func_8001C3|func_8000C0|func_8000C2" /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs
git diff --check
```
