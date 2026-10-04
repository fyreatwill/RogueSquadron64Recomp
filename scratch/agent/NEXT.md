# Next work unit: retail-grounded writer-PC histogram for the target source span

HYPOTHESIS-ID: m5-source-writer-class

Competing hypotheses:

- H1: a retail writer-PC family is active in the target 512-width phase and
  identifies a new legitimate source-writer class to audit in the port.
- H2: retail has target-phase writes to the destination span, but no
  phase-gated writer family survives the histogram; the missing payload is
  upstream of this destination edge.
- H3: the oracle or paired port route fails a positive control or target phase,
  so the writer histogram is unevaluable.

Discriminator: in one build/run, retain the whole-RDRAM positive control and
the existing title/hangar controls, then collect the oracle writer-PC
histogram for physical `0x1798B0..0x179A48` specifically at VI origin
`0x006AB400`, width 512. Pair it with declared/real and legacy/real using the
existing gate/source/PCM diagnostics. H1 requires at least one nonzero
phase-gated retail writer-PC row plus matching qualified port target joins; H2
requires qualified controls and zero target-phase retail writer-PC rows; H3
is any missing positive control, target phase, or port arm.

Commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    # Add to the oracle argument list in the new recipe, after the existing
    # 0x1798B0 watch: --pc-hist-watch 2 --pc-hist-phase 0x006AB400:512
    env RS64_BOUNDARY_OUT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s4018_m5_source_writer zsh scratch/agent/run_s4018_m5_source_writer.sh

The new recipe must launch retail, declared/real, and legacy/real concurrently,
use a fresh output directory, preserve the whole-RDRAM positive control and
phase controls, and SIGKILL every arm after its watchdog. Do not add a gate or
payload mitigation from writer counts; any mitigation-shaped change requires
an `ORIGIN:` naming the writer and stating whether its value is legitimate.
