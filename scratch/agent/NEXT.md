# NEXT work unit — trace the selected M5 direct-writer edge

HYPOTHESIS-ID: m5-direct-writer-edge

Before building, ask the retail oracle for phase-gated execution rows at
`0x8002BEEC` and `0x800078EC`, including predecessor PC and bytes around the
target spans. Use the whole-RDRAM watch as the first positive control and the
title/hangar phase buckets. Then batch one port-side census at the equivalent
writer entry, recording guest return/caller edge and target bytes. Keep the
validated route, output, waits, slots, status handling, consumer dispatch, and
PCM writeback unchanged.

Retail command shape:

    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 180 \
      --watch-write 0x0:0x800000 --watch-pc 0x8002BEEC --watch-pc 0x800078EC \
      --pc-phase-log-width 0x006AB400:512 --pc-phase-log-width 0x00790400:1024

Port command shape, after the instrument is built, from `build/`:

    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
      ROGUESQ_SPIN_YIELD=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
      ROGUESQ_LOG_M5_DIRECT_WRITER=1 ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a' \
      ./RogueSquadron64Recomp

Competing hypotheses:

- `H-PortWriterDispatchAlias`: the port writer reaches the retail edge through
  an overlay/dispatch alias; caller/return evidence identifies the translation.
- `H-PortWriterEarlierMissingEdge`: the port zero-fill remains, but no writer
  edge corresponding to `0x8002BEEC` occurs.
- `H-PortWriterLegitimateZero`: the observed zero fill is a legitimate port
  initialization and the missing nonzero producer is elsewhere.

Discriminator: a port writer row with caller `0x8002BEEC` and matching target
bytes selects dispatch alias/translation; no such row while the zero-fill
persists selects an earlier missing edge; matching writer and zero bytes,
paired with retail nonzero post-store evidence, selects a legitimate-zero
writer with an unlocated later producer. The whole-RDRAM and title/hangar
phase markers must fire or the run is invalid.

Exact constraints: ask the oracle before building; launch the port from
`build/`, use the ROM there, arm the canonical Start schedule, use a
non-dot-prefixed capture path, and terminate with SIGKILL. Do not hand-edit
generated functions. If the port instrument is new, it must include the
whole-RDRAM/title/hangar positive controls in the same run.
