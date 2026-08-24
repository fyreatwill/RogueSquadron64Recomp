# NEXT work unit (s2317) — explicit-route gate/task/wait writer table

HYPOTHESIS-ID: m5-gate-task-wait-contract

## Work unit

Run one repaired, ground-truth-first gate/task/wait checkpoint. Create a
dedicated launcher from the explicit keycode-36 route schedule in
`scratch/agent/run_s2290_m5_stub_route_requal.sh`; do not reuse the s2276
launcher’s incomplete port contract env list. Preserve the retail oracle
preflight and add writer-PC/value attribution for gate, task/output, and wait
watches. Enable the complete port task/gate/slot/PCM table, then run silent
and image arms from the same build, staging image after silent reaches hangar.
No runtime, gate, wait, status, slot, consumer, or default change.

## Competing hypotheses and discriminating measurement

- H-GateWriter-Selected: oracle gate watch `0x000A0F50` has a target-phase
  writer PC/value row, and the matching port arm reaches the gate contract
  branch and downstream task/slot progress.
- H-WaitWriter-Selected: gate and task controls pass, and oracle wait watch
  `0x0001498A` has a target-phase service/voice writer PC/value transition
  with the matching port wait-field change and return.
- H-Gate-Wait-Outside-Target: whole-RDRAM, title/hangar, task/output, route,
  and port contract controls pass, but neither gate nor wait has a target-
  phase writer row. This leaves writer attribution or phase boundaries open.
- H-CoverageInvalid: any whole-RDRAM, title, hangar, task/output, route, or
  complete port-table control is absent. No phase null is interpretable.

The discriminator is one same-run table keyed by oracle watch and port arm:
oracle aggregate hits, `--first-watch` PC/value, `--pc-hist-watch` writer
PCs, and `--pc-hist-phase 0x00790400:1024` plus
`0x006AB400:512`; port gate/task/slot/PCM markers and title/hangar phases.
A positive gate row plus matching port branch selects H-GateWriter-Selected;
a positive wait row plus matching worker/return selects H-WaitWriter-Selected;
task/output positive with both phase writer nulls selects the unresolved
boundary. Any missing positive control selects H-CoverageInvalid.

## Exact commands

1. Add the dedicated launcher with `apply_patch`, based on the s2290 explicit
   key schedule and the s2285 oracle/arm structure. Its oracle command must
   retain `--watch-write 0x0:0x800000`, `--watch-write 0xA0F50:0xA0F54`,
   `--watch-write 0x141AD0:0x141AF0`, and `--watch-write 0x1498A:0x1498B`,
   and add `--first-watch 1 --first-watch 2 --first-watch 3`,
   `--pc-hist-watch 1 --pc-hist-watch 2 --pc-hist-watch 3`,
   `--pc-hist-phase 0x00790400:1024 --pc-hist-phase 0x006AB400:512`, and
   bounded `--post-value-watch 1 --post-value-watch 2 --post-value-watch 3`
   rows. Its port `COMMON` list must
   include `ROGUESQ_LOG_PHASE=1`, `ROGUESQ_LOG_M5_TASK_CONTRACT=1`,
   `ROGUESQ_LOG_M5_GATE_CONTRACT=1`, `ROGUESQ_LOG_FILTER_VOICE_AUDIT=1`,
   `ROGUESQ_LOG_AUDIO_RETURN=1`, `ROGUESQ_LOG_PCM_BOUNDARY=1`,
   `ROGUESQ_LOG_M5_B40_ROUTE=1`, and `ROGUESQ_LOG_M5_ROUTE_STATE=1`.
2. Syntax-check and run it once, without rebuilding:

       zsh -n scratch/agent/run_s2317_m5_gate_task_wait_explicit_pair.sh
       zsh scratch/agent/run_s2317_m5_gate_task_wait_explicit_pair.sh s2317_m5_gate_task_wait_explicit_pair

3. Parse only bounded oracle shutdown summaries and the launcher’s driver
   summary plus phase/contract marker counts. If the repaired launcher still
   lacks a required marker or either arm misses hangar, classify the run
   coverage-invalid; do not add another field or infer from elapsed time.
