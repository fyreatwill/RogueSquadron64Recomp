# NEXT work unit (repair the unified E9 task-key join)

HYPOTHESIS-ID: m3-postsec2-parser-chain

The s795 control run proved authoritative fetch, handler, and State/fullSync
counts in one live row, but the aligned callback did not attach: the same run
reported `e9_aligned=1` in `[dl-sync-probe2]` while every unified control row
had `aligned=0` and `guest_dl=0xFFFFFFFF`.

## Competing hypotheses

- H-callback-key-mismatch: the aligned callback sees a different task serial or
  task lifecycle than task-end. Prediction: paired callback/task-end debug rows
  show unequal keys or a reset between them.
- H-aligned-call-not-reached: the displayed `[dl-sync-probe2]` row is from a
  different binary path or call site. Prediction: callback-entry control rows
  are absent even when probe rows fire.
- H-shared-state-overwrite: the callback writes the aligned fields, then a
  concurrent task/reset overwrites them before task-end. Prediction: callback
  entry has `aligned=1` for the same key, but task-end sees zero and a changed
  current task.

## Discriminating measurement

Add bounded callback-entry and task-end rows for control tasks containing both
the passed task serial and `g_e9prov.task`, plus the aligned count/list. One
run must show which of the three outcomes occurs. Keep the existing four
positive controls and authoritative counters. Do not change parser behavior.

## Exact commands

```sh
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8
env ROGUESQ_LOG_E9_PROVENANCE=1 ROGUESQ_LOG_E9_UNIFIED=1 \
  ROGUESQ_LOG_E9_DISPATCH=1 ROGUESQ_LOG_RDP_ADVANCE=1 \
  ROGUESQ_LOG_DL_SYNC=1 ROGUESQ_LOG_DL_SYNC2=1 \
  PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 \
  PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
  PROBE_KEYS='3:start 7:start 11:start 15:a' \
  zsh tools/probe.sh "$PWD/scratch/agent/soak_results/s796_join" 60 2
```

Expected outcomes: unequal keys select H-callback-key-mismatch; absent
callback-entry rows select H-aligned-call-not-reached; callback `aligned=1`
followed by task-end zero selects H-shared-state-overwrite. Any pre-1024 death
is unevaluable and must not update the parser ledger.
