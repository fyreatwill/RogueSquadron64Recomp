# Next work unit: re-qualify the scheduler boundary with spin-yield enabled

HYPOTHESIS-ID: m5-legacy-staging-schedule-4012

Competing hypotheses:

- H1: with the established default spin-yield route restored, declared/real
  reaches both target phases while legacy/real again crashes after the
  legitimate `0xF80` writer; this supports the legacy staging path as the
  differentiator.
- H2: both arms reach both target phases with matching writer/successor rows;
  the prior crash remains schedule-sensitive or externally nondeterministic.
- H3: declared/real stalls again before target while legacy/real reaches title;
  the arm-dependent route failure is reproducible and the staging crash split
  remains unevaluable.

Discriminator: one Debug build and one concurrent retail-oracle plus
declared/real and legacy/real capture. Retail whole-RDRAM, title VI 1024, and
hangar VI 512 controls must fire. Both port arms must fire the RSP source-hook
and writer controls. Compare phase progress, `[CRASH]`/`[ABORT]`, writer rows,
and opaque scheduler successor rows; do not decode scheduler `a0` as an
OSTask. A positive arm control is not sufficient without the phase controls.

Commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    env RS64_BOUNDARY_OUT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s4014_m5_scheduler_spin1 ROGUESQ_SPIN_YIELD=1 zsh scratch/agent/run_s4012_m5_scheduler_boundary.sh

The output directory must be new. Preserve the writer/scheduler instrumentation
and the concurrent three-arm schedule. If H3 repeats, stop treating the crash
split as qualified and pivot to a new M5 discriminator.
