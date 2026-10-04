# Next work unit: retain retail gate-write values in the M5 discriminator

HYPOTHESIS-ID: m5-gate-source-boundary

Competing hypotheses:

- H1: the retail `0x800A0F50` writes include a target-phase value transition
  and match the port's gate/source/downstream activity; this selects the next
  M5 de-stub candidate.
- H2: retail reaches the target route but its gate writes are initialization-only
  or remain zero; no behavior change is justified.
- H3: reordering/isolation still fails to retain gate values or a control fails;
  the result is unevaluable and the capture must be redesigned again.

Discriminator: use the same oracle invocation and same-build declared/real plus
legacy/real port table as s4016, but put the `0xA0F50` watch before the
whole-RDRAM watch (or otherwise give it a dedicated print budget) so all 17
retail gate-write values and their phase are retained. The whole-RDRAM watch
must still reach its positive-control threshold in that same run. H1 requires
a target-phase retail value transition plus the already observed valid port
gate/source/downstream controls. H2 requires a qualified retail zero or
initialization-only value sequence. H3 is any missing control or remaining
value suppression; do not interpret its nulls.

Commands:

    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 75 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --watch-write 0xA0F50:0xA0F54 --watch-write 0x0:0x800000 --watch-write 0x1798B0:0x179A48 --watch-pc 0x80094648 --pc-phase-log-width 0x00790400:1024 --pc-phase-log-width 0x006AB400:512 --vi-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start
    cmake --build build --config Debug --target RogueSquadron64Recomp
    env RS64_BOUNDARY_OUT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s4017_m5_gate_values zsh scratch/agent/run_s4017_m5_gate_values.sh

The output directory and recipe must be new. Preserve the positive controls and
kill every arm with SIGKILL after the watchdog. Do not change a gate or add a
skip based on a writer count alone; any mitigation-shaped change needs an
`ORIGIN:` naming the legitimate writer and explaining its value.
