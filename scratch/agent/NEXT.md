# Next work unit: test whether scheduler spin changes the legacy boundary

HYPOTHESIS-ID: m5-legacy-staging-schedule-4012

Competing hypotheses:

- H1: disabling host spin-yield exposes the legacy-only `0xF80` staging crash.
- H2: the route remains crash-free, so the prior failure was caused by the
  concurrent spin-yield schedule rather than the staging length itself.
- H3: writer/successor rows remain arm-dependent while outcomes vary, leaving
  an external scheduler race as the discriminator.

Discriminator: one build and one concurrent retail-oracle plus declared/real
and legacy/real capture. The port writer hook fires immediately before the
actual audio ucode-data DMA and records the selected DMA length, task fields,
and a monotonic source sequence; the existing scheduler table records the
opaque task-load successor and send-before rows. The retail oracle adds a
phase-gated task dump at the task-load PC as independent ground truth. Retail's
whole-RDRAM, title, and hangar controls must fire; both port arms must fire
the RSP source-hook control. A legacy-only writer hit before the crash selects
H1; matching writer rows but a legacy-only successor selects H2; matching
writer and successor rows with divergent arm outcome selects H3. Never decode
scheduler `a0` as an OSTask; ABI rows remain authoritative.

Commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_s4013_m5_scheduler_schedule.sh

The current scheduler wrapper is the launch baseline; the next iteration must
set `ROGUESQ_SPIN_YIELD=0` in both port arms, preserve the writer/successor
table, and write summaries under a new
`scratch/agent/s4013_m5_scheduler_schedule/` directory.
