# Next work unit: qualify M5 task-contract logger startup stability

HYPOTHESIS-ID: m5-task-contract-capture-stability

s3836 was coverage-invalid twice: the retail oracle passed whole-RDRAM,
title, and hangar controls and produced 1,165 phase-gated task rows, while
the port crashed at guest `0x8000834C` before VI 320→title with the task
contract rows absent. The next unit must determine whether the logger changes
startup stability before attempting a contract comparison.

Competing hypotheses and discriminator:

- H1: `ROGUESQ_LOG_M5_TASK_CONTRACT=1` changes timing/startup and causes the
  pre-title crash. In one same-build run, the logger-off image arm reaches
  title/hangar while logger-on does not; phase and positive controls must be
  present for the stable arm.
- H2: the crash is unrelated to task-contract logging. Both image arms have
  the same pre-title crash or both reach the target phases, with the same
  startup outcome independent of the logger.
- H3: the A/B is unevaluable. Either arm lacks the whole-run/phase controls,
  or the logger-on arm has no valid launch and no comparable logger-off arm.

Discriminator: build once, launch two concurrent image arms from `build/`,
one with `ROGUESQ_LOG_M5_TASK_CONTRACT=1` and one without it, keeping every
other validated s3835 environment variable identical. Require each arm's
phase control and crash/abort status; do not interpret missing task rows as a
contract result. Use SIGKILL cleanup and retain both logs.

Exact commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_s3837_m5_task_contract_stability.sh

Positive controls: `[phase]` must reach title `0x00790400`/1024 and hangar
`0x006AB400`/512 for any arm used in a contract conclusion; the logger is
diagnostic only and no runtime behavior change is authorized.
