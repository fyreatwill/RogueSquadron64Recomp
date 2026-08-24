# NEXT work unit (s2316) — gate/task/wait writer contract checkpoint

HYPOTHESIS-ID: m5-gate-task-wait-contract

## Work unit

Run the existing ground-truth-first paired checkpoint with no runtime or
contract change. The retail oracle must run and pass its whole-RDRAM control
before either port arm starts. It watches the guest gate `0x800A0F50`, the
task/output span `0x80141AD0:0x80141AF0`, and the wait countdown
`0x8014998A`, while the port runs silent and Factor 5 image arms from the same
build with gate/task/slot/PCM traces. Do not rebuild between arms and do not
change a gate, wait hatch, status store, guard, or default.

## Competing hypotheses and discriminating measurement

- H-GateWriter-Selected: the retail oracle records a target-phase write to
  `0x800A0F50` with a named writer/value transition, and the matching port arm
  records the gate branch and downstream task/slot progress. This selects the
  gate contract as the next boundary.
- H-WaitWriter-Selected: the gate control is positive, but the target-phase
  transition at `0x8014998A` has a named service/voice worker and the port has
  the matching wait-field change and return. This selects the wait contract.
- H-Gate-Wait-Outside-Target: whole-RDRAM, task/output, and route controls are
  positive, but neither gate nor wait has a target-phase writer hit. This
  leaves the writer attribution or phase boundary unresolved and authorizes no
  behavior change.
- H-CoverageInvalid: any whole-RDRAM, title/hangar, task/output, or port-arm
  control is absent. No phase null is interpretable.

The discriminator is one same-run table keyed by arm and phase: oracle gate,
task/output, and wait writer PCs/values; port gate entry/branch, task dispatch
and exit, slot transition, PCM source/consumer, and route phase. A positive
gate row selects H-GateWriter-Selected; a positive wait row with the matching
worker/return selects H-WaitWriter-Selected; both may be selected if both
rows independently close. A complete pair of phase nulls selects the
unresolved-boundary hypothesis only when every positive control passes.

## Exact commands

1. Syntax-check and run the existing paired checkpoint; it performs the oracle
   preflight before launching the two port arms:

       zsh -n scratch/agent/run_s2276_m5_step1_pair.sh
       zsh scratch/agent/run_s2276_m5_step1_pair.sh s2316_m5_gate_task_wait_contract

2. Parse only bounded summaries from
   `scratch/agent/s2316_m5_gate_task_wait_contract/{oracle,silent,image}.log`:
   whole-RDRAM and title/hangar controls, gate/task/wait oracle hits with
   writer PCs and target phase, then the paired port markers for task exit,
   gate/route, slot, PCM, and title/hangar. Record the selected hypothesis
   and any missing control; do not infer from elapsed time.

3. If the existing script is missing a required marker, stop and classify the
   run coverage-invalid rather than adding a diagnostic-only field. Any new
   instrument must be added to a complete gate/task/wait table in one build
   and one paired run.
