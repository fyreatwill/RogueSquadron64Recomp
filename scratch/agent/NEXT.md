# NEXT work unit (s2284) — A1 two-wave route-contention discriminator

HYPOTHESIS-ID: m5-a1-vi-publisher-cadence

## Work unit

Run one same-build, phase-gated two-wave matrix using the existing VI context
and parity-scheduler diagnostics. Keep all runtime defaults unchanged. Launch
the control and alternate-field arms concurrently in wave 1. After both wave-1
processes terminate, launch current-reg-screen and retrace-parity concurrently
in wave 2. Keep one independent retail oracle running across both waves. Stop
each port arm only after its positive all-width controls and either target
origin `0x00696100` or `0x00696600`; retain 15 seconds after the first
`0x00696600` row. Kill every remaining process with SIGKILL.

The four-way s2283 run is not a publisher result: all four arms passed their
positive controls but crashed at guest PC `0x80001F88` in the initial 640 phase.
This wave split is the new route discriminator for that failure.

## Competing hypotheses and discriminating measurement

- H-FourArmContention: the four-way process load caused the s2283 abort. At
  least one two-arm wave reaches a target origin after both positive controls;
  the target rows then make the A1 publisher comparison interpretable.
- H-RouteIntrinsic: both two-arm waves reproduce the initial-640 abort after
  both positive controls, so the current A1 route remains invalid and the
  publisher question stays parked.
- H-ArmSpecificRoute: exactly one wave reaches the target window, selecting a
  behavior-arm or wave-specific route sensitivity that must be isolated before
  publisher inference.
- H-NoPublisher: both waves qualify target rows, but neither callback/field
  relation predicts the observed second-origin rows; retain the publisher as
  unobserved rather than changing a default.

The single discriminating table is keyed by wave, arm, callback ordinal,
total_vis, delta, callback parity, total parity, selected field, current line,
committed origin, and skipped-VI count. Require every arm to have its
`[vi-context-port-control]` and `[vi-parity-scheduler-control]` rows before
interpreting any target-origin null. A publisher is not selected unless a
target-qualified wave supplies reproducible second-origin rows whose parity or
timing relation predicts the other target-qualified arm. The retail oracle must
pass whole-RDRAM `>=10,000` writes and show both title and hangar origins.

## Exact commands

1. Create `scratch/agent/run_s2284_m5_vi_publisher_two_wave.sh` with
   `apply_patch`. Base its process/watchdog structure on
   `scratch/agent/run_s2283_m5_vi_publisher_matrix.sh`. Use the same oracle
   command with `--watch-write 0x0:0x800000`, `--vi-trace`, the Rice video
   plugin, and the established eleven-Start `--press` schedule. Each port arm
   must set `ROGUESQ_AUDIO_UCODE=0`, `ROGUESQ_SPIN_YIELD=1`,
   `ROGUESQ_LLE_UNGATED=1`, `ROGUESQ_LLE_SOLO=1`, `ROGUESQ_LOG_PHASE=1`,
   `ROGUESQ_LOG_VI_CONTEXT_PORT=1`, `ROGUESQ_LOG_VI_PARITY_SCHEDULER=1`,
   and `ROGUESQ_LOG_VI_TRANSITION=1`, plus exactly its behavior-arm setting.
2. Run from the repository root:
   `zsh scratch/agent/run_s2284_m5_vi_publisher_two_wave.sh s2284_m5_vi_publisher_two_wave`
3. Summarize with bounded `grep`/`tail` only: retail positive controls, each
   arm's two runtime controls, target-origin rows, parity tuples, terminal
   phase, and crash/timeout. Do not infer a publisher from an arm or wave that
   lacks its positive controls.
