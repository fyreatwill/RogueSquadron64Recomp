# NEXT work unit (s1045)

HYPOTHESIS-ID: retail-phase-path-discriminator

Run one new independent retail-oracle phase-path discriminator. Do not arm
the freelist watch unless the same run first reaches the 512 hangar phase.
Use the existing oracle harness and a whole-RDRAM write watch as the positive
control; capture independent VI poll/callback and PIF traces. Do not modify
runtime code.

## Competing hypotheses and discriminator

* `H-input-contract`: the retail phase path requires a control/state sequence
  not represented by Start-only or Start+A events.
* `H-oracle-phase`: the retail core/input plugin remains on its documented
  attract path regardless of the tested input sequence.
* `H-transition-observation`: the transition occurs but the current VI
  observation path misses it.

Discriminating measurement: an independent VI poll and callback must agree on
whether width 512 (or another non-320 phase) occurs after scripted input; the
whole-RDRAM watch and PIF trace must be positive in the same run. A matching
non-320 transition selects H-transition-observation only if both VI sources
agree; no transition with positive controls selects H-input-contract/oracle-
phase and leaves the missing state sequence open.

## Exact commands

```sh
sed -n '1,220p' tools/oracle/README.md
find scratch/agent/soak_queue -maxdepth 1 -type f -name '*.sh' -print
rg -n "vi-poll|vi-trace|pif-trace|whole-RDRAM|Start|hold-ms" tools scratch/agent/*.sh
# Copy/edit one self-contained recipe under scratch/agent/soak_queue/;
# launch the retail oracle, watchdog it, SIGKILL its process group, and record
# VI callback/poll, PIF, and whole-RDRAM-control counts.
```
