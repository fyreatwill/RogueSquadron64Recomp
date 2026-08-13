# NEXT work unit (stable post-sec2 capture for the unified E9 task-key join)

HYPOTHESIS-ID: m3-postsec2-parser-chain

The s796 run built the callback/task-end join trace but died at VI 640. It
reported no parser rows, so the join remains untested in this iteration.

## Competing hypotheses

- H-prechain-transient: the run dies before the parser chain is sampled.
  Prediction: no VI-1024 gate or parser positive-control rows.
- H-callback-key-mismatch: the aligned callback sees a different task serial
  or task lifecycle than task-end. Prediction: paired rows at VI 1024 show
  unequal passed/current serials.
- H-shared-state-overwrite: the callback writes aligned fields, then a reset
  overwrites them before task-end. Prediction: callback entry and task-end rows
  share a serial, but task-end has zero/`0xFFFFFFFF`.

## Discriminating measurement

Run two concurrent, identical phase-gated post-sec2 captures with the join
instrument already built. Require VI 1024 and all four controls
(`emit/raw/dispatch/match`) before interpreting join rows. A pre-1024 death
selects only H-prechain-transient and leaves the join unevaluable; unequal
serials select H-callback-key-mismatch; equal callback/task-end serials with a
lost aligned value select H-shared-state-overwrite.

## Exact commands

```sh
for arm in s797_join_a s797_join_b; do
  env ROGUESQ_LOG_E9_PROVENANCE=1 ROGUESQ_LOG_E9_UNIFIED=1 \
    ROGUESQ_LOG_E9_DISPATCH=1 ROGUESQ_LOG_RDP_ADVANCE=1 \
    ROGUESQ_LOG_DL_SYNC=1 ROGUESQ_LOG_DL_SYNC2=1 \
    PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=240 \
    PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
    PROBE_KEYS='3:start 7:start 11:start 15:a' \
    zsh tools/probe.sh "$PWD/scratch/agent/soak_results/$arm" 60 2 &
done
wait
```

Build is already complete; do not rebuild unless the source changes. Any
pre-1024 death is unevaluable for the join and must not update the parser ledger.
