# NEXT work unit (s2319) — M5 slot/status transition census

HYPOTHESIS-ID: m5-slot-status-transition-census

## Work unit

Run one same-build, ground-truth-first explicit keycode-36 staged pair with
the existing stub and Factor 5 image arms. Add the existing
`ROGUESQ_LOG_VI_CALLERS=1` table to the launcher so slot allocation, slot-byte
writes, key-on, and descriptor initialization are recorded. Retain the
all-fifteen-bucket oracle gate/task/wait table and every current task, gate,
route, image-stage, and PCM marker. Make no runtime, gate, wait, slot, guard,
consumer, or default change.

## Competing hypotheses and discriminating measurement

- H-Slot-Transition: the image arm reaches a valid slot `01/02/00` transition
  with a named writer and matching task/PCM ordering; the stub remains the
  no-DMEM/no-slot control.
- H-Task-Only: oracle and port task/DMEM/DMA/PCM controls are positive, but no
  valid port slot transition or descriptor/key-on sequence occurs.
- H-Gate-Branch: the two port arms diverge in the gate/route table before slot
  work, identifying the gate branch as the remaining arm-specific boundary.
- H-CoverageInvalid: whole-RDRAM, all-fifteen oracle phase buckets, title,
  hangar, or either arm's contract controls are absent.

The discriminator is one phase-keyed table per arm containing slot allocation,
slot-byte writes (especially new values `01`, `02`, and `00`), key-on and
descriptor rows, task/DMA/service rows, PCM source/consumer joins, gate/route
markers, and the independent oracle gate/task/wait writer/value table. A
named slot transition with downstream ordering selects H-Slot-Transition;
positive task/PCM without it selects H-Task-Only; an arm-specific gate/route
divergence selects H-Gate-Branch. Any missing positive control is
H-CoverageInvalid and makes nulls unevaluable.

## Exact commands

1. Use `apply_patch` to add `ROGUESQ_LOG_VI_CALLERS=1` to the `COMMON` array in
   `scratch/agent/run_s2317_m5_gate_task_wait_explicit_pair.sh`. Do not remove
   any existing env var or oracle phase/watch flag.
2. Run:

       zsh -n scratch/agent/run_s2317_m5_gate_task_wait_explicit_pair.sh
       zsh scratch/agent/run_s2317_m5_gate_task_wait_explicit_pair.sh s2319_m5_slot_status_transition_census

3. Parse only bounded oracle shutdown rows and the launcher driver summary plus
   per-arm phase/slot/task/PCM marker counts. Require whole-RDRAM `10000+`,
   all fifteen positive oracle buckets, title/hangar coverage, and both port
   hangar phases before interpreting any slot null. Do not change behavior from
   a null result.
