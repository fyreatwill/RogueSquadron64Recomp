# NEXT work unit (s2318) — all-origin gate/task/wait writer census

HYPOTHESIS-ID: m5-gate-task-wait-origin-census

## Work unit

Run one repaired, ground-truth-first gate/task/wait checkpoint using the
explicit keycode-36 staged route from s2317. Expand the oracle’s phase table
from title/hangar to all fifteen observed VI origins, while retaining the
whole-RDRAM, gate, task/output, wait, first-value, PC-histogram, and
post-value controls. Keep both port arms in the same launcher and preserve
the complete task/gate/slot/PCM marker set. No runtime, gate, wait, status,
slot, consumer, or default change.

## Competing hypotheses and discriminating measurement

- H-Earlier-Origin: a gate, task, or wait writer appears in one of the
  thirteen previously observed non-title/hangar origins, with a matching
  oracle value/PC and port branch or return marker.
- H-Phase-Attribution-Gap: whole-RDRAM, gate/task controls, all fifteen VI
  buckets, and both port hangar phases pass, but no gate or wait writer PC
  appears in any bucket. The writer is outside the callback windows or the
  phase join is incomplete.
- H-Task-Only: task/output retains a writer row while gate and wait remain
  null across all buckets, preserving a task boundary without selecting a
  gate/wait writer.
- H-CoverageInvalid: any whole-RDRAM, title, hangar, task/output, route, or
  complete port-table control is absent.

The discriminator is one same-run table keyed by all fifteen oracle phase
buckets and watches 1–3: callback count, writer-PC histogram, first/value
rows, and post-value samples, joined with each port arm’s gate/route/task/
PCM markers. A positive earlier-origin writer with a matching port transition
selects H-Earlier-Origin. Positive controls with no gate/wait row in all
fifteen buckets select H-Phase-Attribution-Gap; task-only rows select
H-Task-Only. Any missing control is H-CoverageInvalid.

## Exact commands

1. Use `apply_patch` to modify
   `scratch/agent/run_s2317_m5_gate_task_wait_explicit_pair.sh` by adding
   these repeatable oracle flags alongside its existing two phase flags:

       --pc-hist-phase 0x006AB800:512
       --pc-hist-phase 0x00656400:512
       --pc-hist-phase 0x00656800:512
       --pc-hist-phase 0x0066A500:640
       --pc-hist-phase 0x00696100:640
       --pc-hist-phase 0x0066AA00:640
       --pc-hist-phase 0x00696600:640
       --pc-hist-phase 0x00000280:320
       --pc-hist-phase 0x006BA280:320
       --pc-hist-phase 0x005D4500:640
       --pc-hist-phase 0x0062C200:640
       --pc-hist-phase 0x0062BD00:640
       --pc-hist-phase 0x00790800:1024

   The existing `0x00790400:1024` and `0x006AB400:512` flags complete
   the fifteen-bucket table. Do not remove the oracle positive control or
   any existing watch/value flag.
2. Syntax-check and run without rebuilding:

       zsh -n scratch/agent/run_s2317_m5_gate_task_wait_explicit_pair.sh
       zsh scratch/agent/run_s2317_m5_gate_task_wait_explicit_pair.sh s2318_m5_gate_task_wait_origin_census

3. Parse only bounded oracle shutdown summaries and the launcher driver
   summary plus per-arm phase/contract marker counts. Require whole-RDRAM
   `10000+`, title/hangar coverage, task/output writes, and both port hangar
   phases before interpreting any phase null. Do not change behavior from a
   null result.
