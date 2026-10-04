# Next work unit: qualify the next M5 gate/source discriminator

HYPOTHESIS-ID: m5-gate-source-boundary

Competing hypotheses:

- H1: a retail writer/value transition at the remaining `0x80094648` gate/source
  boundary precedes a valid nonzero audio path and selects the next de-stub.
- H2: retail reaches the target route but the gate/source values remain zero or
  are written only by already-accounted-for initialization paths; no behavior
  change is justified.
- H3: the retail run does not reach the target phase or the gate watch is not
  an active consumer; the question is unevaluable and must be redesigned.

Discriminator: first obtain independent retail ground truth in one oracle run,
with the whole-RDRAM positive control, title/hangar VI controls, phase-gated
watches for `0x800A0F50` and the `0x80094648` writer/value path, and the
existing source-span watch `0x1798B0:0x179A48`. Then run the same-build port
control with the existing task/source/PCM joins. H1 requires a retail writer
and value transition in the target phase plus a matching valid port gate and
downstream slot/PCM control. H2 requires the controls and a qualified zero or
initialization-only result. H3 is any missing phase or positive control; do not
interpret its nulls.

Commands:

    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 75 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --watch-write 0x0:0x800000 --watch-write 0xA0F50:0xA0F54 --watch-write 0x1798B0:0x179A48 --watch-pc 0x80094648 --pc-phase-log-width 0x00790400:1024 --pc-phase-log-width 0x006AB400:512 --vi-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start
    cmake --build build --config Debug --target RogueSquadron64Recomp
    env RS64_BOUNDARY_OUT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s4016_m5_gate_source zsh scratch/agent/run_s4016_m5_gate_source.sh

The output directory and recipe must be new. Preserve the positive controls and
kill every arm with SIGKILL after the watchdog. Do not change a gate or add a
skip based on a writer count alone; any mitigation-shaped change needs an
`ORIGIN:` naming the legitimate writer and explaining its value.
