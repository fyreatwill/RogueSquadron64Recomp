# Next work unit: inspect the legacy-only scheduler failure

HYPOTHESIS-ID: m5-legacy-real-route-4009

Competing hypotheses:

- H1: the legacy `0xF80` DMEM staging arm corrupts scheduler-visible state before the first audio task; declared/real remains the same-build control.
- H2: a legacy-only scheduler/message successor or queue-state difference causes the `spTaskSchedulerThread+9632` failure, independent of the declared OSTask contract.
- H3: the split is nondeterministic route instability; a repeat with the same table changes which arm fails or makes both arms fail before target phases.

Discriminator: one build and one concurrent declared/real plus legacy/real capture, retaining the retail whole-RDRAM positive control, title/hangar phase controls, the RSP source-hook control, and the phase-scoped scheduler table. Join the last scheduler message/successor row to the existing `audtask-abi` rows. A repeatable legacy-only failure with a changed last successor selects H2; a legacy-only failure immediately after a staging-specific task row selects H1; arm-to-arm outcome changes select H3. Do not treat scheduler `a0` as an OSTask pointer.

Commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_s4009_m5_scheduler_boundary.sh

The script must launch both port arms concurrently, run the retail oracle with
the whole-RDRAM positive control and both target VI origins, kill all children
with SIGKILL, and summarize only bounded markers from
`scratch/agent/s4009c_m5_scheduler_boundary/`.
