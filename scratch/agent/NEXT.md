# Next work unit: isolate process topology from the shared silent scheduler defect

HYPOTHESIS-ID: m5-shared-scheduler-topology

Session 4068 selected Hshared-scheduler: native-SDL silent and
`SDL_AUDIODRIVER=dummy` silent arms both crashed at the same
`spTaskSchedulerThread+9632` fault before either target phase. The next unit
must use the same build and retail positive control, but launch the two silent
arms sequentially so concurrent process topology is no longer shared.

Competing hypotheses:

- Htopology: the matching concurrent crashes are caused by two port processes
  contending for a shared host/runtime resource; sequential arms will change
  the result, with at least one reaching title 1024 and hangar 512.
- Hguest-state: the defect is deterministic inside each process's common guest
  scheduler/state path; both sequential arms will reproduce the same
  pre-target `spTaskSchedulerThread+9632` crash and fault signature.
- Hnative-residual: native SDL has an independent startup effect hidden by the
  concurrent crash; sequential native will fail while sequential dummy reaches
  both target phases.
- Hroute-schedule: termination is schedule-sensitive even sequentially; mixed
  or non-repeatable outcomes are unevaluable and require a new breadcrumb.

Discriminating measurement: one build, one retail-gated capture, then launch
the silent native arm, SIGKILL it after its terminal phase/crash/timeout, and
launch the silent dummy arm under the same phase gates and scheduler/task-route
breadcrumbs. The retail whole-RDRAM positive-control threshold must fire. Both
arms reproducing the same fault selects Hguest-state; one or both arms reaching
both target phases only when sequential selects Htopology; native-only failure
selects Hnative-residual; mixed/unstable termination selects Hroute-schedule.
Do not interpret host queue, drain, or sink output unless an arm reaches both
target phases.

Exact commands:

1. Create `scratch/agent/run_s4069_m5_sequential_silent.sh` from
   `run_s4068_m5_native_dummy_silent.sh`, changing the concurrent `run_port`
   launch into a sequential `run_one` call. Keep
   `ROGUESQ_AUDIO_UCODE=0`, `ROGUESQ_LLE_FORCE=1`, `ROGUESQ_LLE_UNGATED=1`,
   `ROGUESQ_LLE_SOLO=1`, all phase gates, and the scheduler/task-route logs.
2. Run `zsh scratch/agent/run_s4069_m5_sequential_silent.sh` from the repo
   root. Use SIGKILL for each port process and retain separate native/dummy
   logs plus a driver summary.
3. Record the retail positive-control marker, each arm's phase markers, crash
   PC/fault/guest PC, and scheduler breadcrumbs. Update the ledger and truth
   only from the discriminating outcome.
