# Next work unit: isolate the legacy-only 0xF80 staging boundary

HYPOTHESIS-ID: m5-legacy-staging-writer-boundary-4011

Competing hypotheses:

- H1: the legacy-only `staging=0xF80` value is written by the staging path
  immediately before the scheduler crash.
- H2: staging is legitimate, but the legacy route hands a different successor
  message/task to the scheduler and that successor causes the crash.
- H3: writer and successor rows match across declared and legacy arms; the
  route failure is nondeterministic or external to this boundary.

Discriminator: one build and one concurrent retail-oracle plus declared/real
and legacy/real capture. Add a phase-scoped writer watch for the field that
produces the legacy `0xF80` staging value, and log the immediate task-load
successor as an opaque message identity plus its source sequence. Retail's
whole-RDRAM, title, and hangar controls must fire; both port arms must fire
the RSP source-hook control. A legacy-only writer hit before the crash selects
H1; matching writer rows but a legacy-only successor selects H2; matching
writer and successor rows with divergent arm outcome selects H3. Never decode
scheduler `a0` as an OSTask; ABI rows remain authoritative.

Commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_s4009_m5_scheduler_boundary.sh

The current scheduler wrapper is the launch baseline; the next iteration must
add the writer/successor table before running it and write summaries under a
new `scratch/agent/s4012_m5_scheduler_boundary/` directory.
