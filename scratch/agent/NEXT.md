# Next work unit: split legacy scheduler behavior by spin-yield arm

HYPOTHESIS-ID: m5-legacy-staging-schedule-sensitivity

Competing hypotheses:

- H1: only the legacy arm with spin-yield disabled stalls or crashes; spin-yield
  is the route discriminator.
- H2: both legacy spin arms reach both target phases with the same writer and
  successor values; spin-yield is not sufficient and the old crash remains
  nondeterministic.
- H3: declared/real diverges again while both legacy arms match; the failure is
  not attributable to legacy staging or spin-yield.

Discriminator: one Debug build and one concurrent retail-oracle plus three port
arms: declared/real with spin-yield 1, legacy/real with spin-yield 1, and
legacy/real with spin-yield 0. Retail whole-RDRAM, title VI 1024, and hangar VI
512 controls must fire. Every port arm must fire the RSP source-hook and writer
controls. Compare phase progress, `[CRASH]`/`[ABORT]`, writer rows, and opaque
scheduler successor rows; do not decode scheduler `a0` as an OSTask. A positive
arm control is not sufficient without the phase controls.

Commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    env RS64_BOUNDARY_OUT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s4015_m5_scheduler_spin_split zsh scratch/agent/run_s4015_m5_scheduler_spin_split.sh

The output directory and recipe must be new. Preserve the writer/scheduler
instrumentation and kill every arm with SIGKILL after the watchdog. If H2
repeats, park the old crash split and move to the next M5 discriminator rather
than repeating this table.
