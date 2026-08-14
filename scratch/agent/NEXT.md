# NEXT work unit (s1145)

HYPOTHESIS-ID: m3-generated-boundary-anomaly

Run one bounded phase-gated stability test using the regenerated binary from
s1143. Do not change code or add a runtime guard. The s1144 attempt reached
only VI width 640 and omitted the explicit E9/slot-dispatch control categories,
so it was unevaluable.

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
env ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_E9_PROVENANCE=1 ROGUESQ_LOG_E9_UNIFIED=1 ROGUESQ_LOG_SLOT_DISPATCH=1 \
  PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
  zsh tools/probe.sh scratch/agent/next_s1145 300 1
grep -n 'vi_width=1024\|\[e9-prov\].*scope=control\|\[e9-unified\]\|\[slot-dispatch\]\|slotDispatcherIter+872\|\[CRASH\]' \
  scratch/agent/next_s1145/run.log | tail -60
```

Expected outcomes:

- PASS/H1: target phase and controls are reached and the boundary-sensitive
  crash outcome changes relative to the established recurrence.
- RECURRENCE/H2: controls and target phase are reached, then the same
  `slotDispatcherIter+872` SIGBUS recurs; do not mitigate it.
- UNEVALUABLE: no positive control or no target phase; report that instead of
  interpreting a null crash marker.
