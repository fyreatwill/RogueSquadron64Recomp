# Next work unit: qualify both target phases with the task-contract logger

HYPOTHESIS-ID: m5-task-contract-capture-stability

s3837 refuted logger-induced pre-title instability: the same-build logger-off
and logger-on image arms both reached title VI `0x00790400`/1024 with no
crash/abort. Logger-on emitted 2,406 task-contract rows; logger-off emitted
none. Neither reached hangar VI `0x006AB400`/512 before the watchdog, so the
contract comparison remains unevaluable at the target scope.

Competing hypotheses and discriminator:

- H1: The logger changes post-title scheduling and prevents hangar reachability.
  Logger-off reaches hangar while logger-on does not, with both arms' phase
  controls positive.
- H2: The logger is harmless; both arms reach hangar or both stop before it,
  with no crash/abort and identical phase outcomes.
- H3: The pair is coverage-invalid. Either arm lacks its phase control, or a
  crash/abort prevents a comparable target-phase result.

Discriminator: preserve the s3837 environment and script, extend only the
watchdog to 180 seconds, and run logger-off/logger-on concurrently in one
build. Require title and hangar phase markers in both logs. Do not interpret
task rows unless the arm reaches hangar.

Exact commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_s3838_m5_task_contract_target_stability.sh

Positive controls: each arm must show `[phase]`, title origin
`0x00790400`/1024, and hangar origin `0x006AB400`/512, with no `[CRASH]` or
`[ABORT]`. Use SIGKILL cleanup.
