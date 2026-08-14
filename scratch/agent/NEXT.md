# NEXT work unit (s1104)

HYPOTHESIS-ID: submit-producer-boundary

Perform one bounded runtime-free audit of the remaining gate ownership for the
two queue pairs. Trace the writers/readers of the SP task-state bytes guarding
`spTaskSchedulerThread`'s `0x8011A818` send and the DP flag guarding
`dpInterruptHandlerThread`'s `0x8011A7E8` send, and compare them with the
consumer-side gates. Do not change queue behavior or build.

Competing hypotheses:

* H-gate-writer: the producer gate is written by the expected scheduler/DP
  lifecycle and can be correlated with the consumer gate.
* H-gate-stale: a clear/reset or missing writer can leave the producer send
  suppressed while the consumer blocks.
* H-gate-alias: the apparent gate is an alias/object field, so its ownership
  cannot be assigned from the fixed-address census.

Discriminator: for each gate, enumerate every generated read and write and
the controlling lifecycle branch. A same-lifecycle writer/read selects
H-gate-writer; a clear without a matching set or an independently stale flag
selects H-gate-stale; an object/index-derived access selects H-gate-alias.
Computed calls must name their exact target boundary rather than infer
reachability.

Exact commands:

```sh
rg -n -C 8 "0x8011A89D|0x8011A89E|0x80019ED4|0x80019EE4|0x8001C3C4|0x8000C0A4|0x8000C2A8" /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs docs/game-architecture.md
rg -n -C 5 "MEM_[BWL].*(5762|5763|5764|72BC|72C0|72C4|72C8|72CC)|lbu.*(5762|5763|5764|72BC|72C0|72C4|72C8|72CC)|sb.*(5762|5763|5764|72BC|72C0|72C4|72C8|72CC)" /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs
git diff --check
```
