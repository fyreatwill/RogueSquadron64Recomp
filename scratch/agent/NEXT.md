# NEXT work unit (s1144)

HYPOTHESIS-ID: m3-generated-boundary-anomaly

Run one bounded phase-gated stability test using the regenerated binary from
s1143. Do not change code or add a runtime guard.

Competing hypotheses and discriminator before the run:

- H1/runtime-relevant boundary: the corrected split changes the recurring
  `slotDispatcherIter+872` SIGBUS outcome during a VI-phase-gated run.
- H2/runtime-independent recurrence: the same SIGBUS recurs with controls and
  phase progression, leaving runtime frame corruption open despite the static
  correction.

Discriminating measurement: one run's phase marker and crash classification,
with positive controls visibly firing. A changed crash outcome selects H1; an
in-phase recurrence selects H2. A pre-phase crash is unevaluable.

```sh
env ROGUESQ_LOG_ALL=1 zsh tools/run-one-stability.sh 300 scratch/agent/next_s1144.log
grep -n 'VI 1024\|slotDispatcherIter+872\|CRASH\|control' scratch/agent/next_s1144.log | tail -40
```

Expected outcomes:

- PASS/H1: target phase and controls are reached and the boundary-sensitive
  crash outcome changes relative to the established recurrence.
- RECURRENCE/H2: controls and target phase are reached, then the same
  `slotDispatcherIter+872` SIGBUS recurs; do not mitigate it.
- UNEVALUABLE: no positive control or no target phase; report that instead of
  interpreting a null crash marker.
