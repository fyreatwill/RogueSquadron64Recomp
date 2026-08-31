# NEXT work unit — redesign the scheduler-safe pointer-source capture

HYPOTHESIS-ID: m5-callback-indirect-pointer-source

Session 3341 added a regeneration-safe probe at the concrete port store
`0x80091900` and observed `0x80007910`, but two retries crashed in the
scheduler before target phases. Retail's requested `0x001099D4` watch passed
the positive control and remained at zero writes; the actual generated load
address is physical `0x001499D4`.

Competing hypotheses remain:

- `H-PointerWriter`: a guest writer sets the indirect callback pointer.
- `H-StalePointer`: the port's pointer is pre-existing/stale and the indirect
  call is only a consumer.
- `H-HostDispatch`: a host/runtime path supplies the pointer.

The discriminating measurement remains a same-run writer census with retail
and port arms plus whole-RDRAM positive controls, but the port route must first
reach title 1024 and hangar 512. A target-phase retail writer at the actual
physical slot identifies `H-PointerWriter`; no retail writer but a target-phase
port writer selects `H-StalePointer`; no writer in either arm with valid
indirect transfers selects `H-HostDispatch`. A null is invalid unless the
whole-RDRAM control fires.

The s3342 control showed that the no-probe route reaches title/hangar, while
enabling the callback-writer logger crashes `spTaskSchedulerThread` before
target VI. The logger is therefore not a valid target-phase instrument on this
recipe. The next single work unit is to redesign that existing probe to record
the complete writer table without scheduler-sensitive per-event output, then
build once and run the same concurrent control/probe arms:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    env ROGUESQ_LOG_M5_CALLBACK_WRITER=1 zsh scratch/agent/run_s3333_m5_callback_reachability.sh

The positive-control rows must include host-boundary and task-handoff controls,
and the probe arm must reach title 1024 and hangar 512. If the redesigned
probe reaches both phases and records the store table, resume the pointer
writer discriminator. If it still crashes while the no-probe arm remains
valid, classify the probe as perturbing and redesign once more; do not infer a
pointer source. No behavioral change is authorized.

Before the route rebuild, the scheduler failure has these competing hypotheses:

- `H-SchedulerData`: the new probe changed generated scheduler data/control
  flow or exposed a bad guest value, so the baseline and instrumented route
  differ before VI-1024.
- `H-SchedulerRuntime`: the crash is an existing runtime/submodule scheduler
  failure independent of the pointer probe; the same failure appears in a
  no-probe control built from the current tree.
- `H-SchedulerRoute`: the recipe's LLE/solo/spin-yield route is the trigger,
  and the normal validated image route remains target-valid.
- `H-Environmental`: the binary/ROM/build or stale process state is invalid;
  a clean build plus the documented launch directory and controls changes the
  outcome.

The discriminating measurement is one same-build, same-run control matrix:
baseline/no new probe, current probe, and normal validated image route, all
with host/task/phase positive controls. A crash only in the probe arm selects
`H-SchedulerData`; matching baseline/probe crashes select
`H-SchedulerRuntime`; only the LLE/solo recipe crash selects `H-SchedulerRoute`;
all arms must reach their expected VI controls before the pointer-source run is
repeated. A missing positive control makes that arm invalid, not a null result.
