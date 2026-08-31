# NEXT work unit — rerun M5 slot/status qualification on validated hangar route

HYPOTHESIS-ID: m5-slot-status-contract-gap

Session 3347 was route-invalid: the current `run_s3327` arm passed host/task/PCM
controls and reached title VI 1024, but never reached VI 512, so it selected
none of the slot/status hypotheses. Use the already validated extended
Start/spin-yield route that reaches hangar, while retaining the same slot,
status, and named-consumer measurements.

Competing hypotheses:

- `H-PortSlotStatusMissing`: the reachable port hangar lacks the retail writer
  or status transition.
- `H-PortConsumerUnreached`: the port writes the state, but the named consumer
  path is not reached.
- `H-PortProbeGap`: both edges run, but the current instrumentation misses them.

Discriminator: a target-phase writer plus consumer hit selects a complete port
edge; writer rows without consumers select `H-PortConsumerUnreached`; neither
writer nor consumer with positive controls selects `H-PortSlotStatusMissing`;
positive consumer-PC controls with no target rows select `H-PortProbeGap`.
If VI 512 is absent again, classify the run route-invalid and select nothing.

Exact commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/soak_queue/done/s1949_menu_input_yield_20260818-021858.sh

Do not change behavior or add a mitigation. The positive controls must fire in
the same run before interpreting any null target result.
