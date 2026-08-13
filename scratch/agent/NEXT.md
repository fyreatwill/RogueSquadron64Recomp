# NEXT work unit (unified phase-5 E9 accounting capture)

HYPOTHESIS-ID: m3-postsec2-parser-chain

The s794 audit found that the prior aligned and authoritative numbers have
different scopes and reset rules. The next unit is one bounded instrumentation
change plus one phase-gated run that records all three counters against the
same task identity; do not add a mitigation.

## Competing hypotheses

- H-authoritative-advance-loss: a same-task aligned E9 is emitted but no
  authoritative fetch follows it. Prediction: `aligned=1, fetched=0` for the
  same guest-list/task identity.
- H-phase-co-gate: aligned and authoritative counts agree within each task,
  while only a subset of phase-5 tasks reaches State/fullSync. Prediction:
  unified records have `aligned=fetched`, with gaps only between task records.
- H-parser-measurement: the old comparison was invalid, but the unified
  capture will still show an address/list identity mismatch. Prediction:
  same-task records cannot be joined without a new explicit task/list key.

## Discriminating measurement

In one build/run, tag the phase-5 aligned-walker record with the same LLE task
and guest-list identity used by authoritative fetch, then log aligned count,
fetch count, handler count, and State/fullSync count in one bounded row. A
same-task aligned-without-fetch row selects H-authoritative-advance-loss;
task-level equality with missing later stages selects H-phase-co-gate; inability
to join the rows selects H-parser-measurement. The positive control must fire
in the same run before any null is interpreted.

## Exact commands

```sh
rg -n "e9_aligned|rs64_rdp_advance|authoritative_fetch|fullsync_dispatch|e9-dispatch|rdp-fullsync" \
  src lib tools
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8
env ROGUESQ_LOG_DL_SYNC2=1 ROGUESQ_LOG_RDP_ADVANCE=1 ROGUESQ_LOG_E9_DISPATCH=1 \
  PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh tools/probe.sh
```
