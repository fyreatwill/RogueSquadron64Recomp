# Session 5320 M4 stage-timing comparison

This was the mandatory new-angle revisit after the preceding 15 ledger titles
were all generated-symbol sweep steps. It used the existing qualified captures;
no build or soak was needed.

Inputs and controls:

- Retail `scratch/agent/m4_task_join_run/`: `3,020,766` mid-task records,
  `2,083` graphics task-end records, all `2,083` task serials joined, four VI
  width controls, and two whole-RDRAM watch controls. Retail had `1,222` of
  `2,083` graphics tasks with a sampled `0x8000` lane and zero task-end tasks
  with that lane.
- Port `scratch/agent/m4_port_task_join_20261017f/port.log`: `324,688`
  phase-5 stage rows, `59` phase-5 task-end rows, and `56` tasks with both a
  stage row and an end row. The capture's VI-512 and probe controls passed in
  the prior task-join qualification.

Port phase-5 result:

| stage | rows | tasks | tasks with `0x8000` |
|---:|---:|---:|---:|
| 10 | 83,266 | 56 | 55 |
| 11 | 83,271 | 56 | 55 |
| 12 | 83,271 | 56 | 0 |
| 13 | 74,880 | 56 | 0 |

The port therefore shows the transient only in stages 10/11, with no
task-end `0x8000` lanes. That is qualitatively consistent with retail's
mid-task-only result, but it is not a retail-equivalent stage comparison:
retail's task-keyed dump exposes instruction PCs, not the port's synthetic
stage labels, and the port covers only 56 of 59 phase-5 end tasks versus 572
retail 512-wide tasks in the corresponding oracle route.

Discriminator outcome: H3, unevaluable at this boundary. The result rules out
“the port retains `0x8000` through the task end” and supports transient
pre-clear timing, but it does not select an accumulator implementation
divergence or equivalence. No mitigation or accumulator rewrite is authorized.

The next useful M4 probe must provide a complete task-keyed port sampler at a
retail-comparable instruction/step boundary, or the thread remains parked.
