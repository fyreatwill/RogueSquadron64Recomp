# NEXT work unit — phase-qualified M5 direct-writer edge census

HYPOTHESIS-ID: m5-direct-writer-edge

Before building, ask the retail oracle for writer ground truth, then build one
port census containing the existing phase, audio-task, callback, PCM, and
static-rs_memset controls plus direct-writer edge fields. Run from `build/`
through `tools/probe.sh`; do not change output or audio behavior.

Retail command shape:

    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 180 \
      --watch-write 0x0:0x800000 --watch-pc 0x8002BEEC --watch-pc 0x800078EC \
      --pc-phase-log-width 0x006AB400:512 --pc-phase-log-width 0x00790400:1024

Port route shape:

    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
      ROGUESQ_SPIN_YIELD=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
      ROGUESQ_LOG_M5_CALLBACK_WRITER=1 ROGUESQ_LOG_PCM_BOUNDARY=1 \
      ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a' \
      ./RogueSquadron64Recomp

Competing hypotheses:

- `H-DispatchAlias`: port reaches `0x800078EC` with caller edge
  `0x8002BEEC` and matching target bytes; the gap is dispatch/translation.
- `H-EarlierProducerGap`: port zero-fill persists with no
  `caller=0x8002BEEC` writer edge; the missing edge is upstream.
- `H-LegitimateZeroThenProducer`: port reaches the matching writer edge but
  stores zero while retail independently stores nonzero bytes; a later producer
  remains unlocated.

Discriminator: compare phase-qualified retail rows at `0x800078EC` and
`0x8002BEEC` with port writer rows. Matching caller and bytes selects
`H-DispatchAlias`; persistent port zero-fill without the caller edge selects
`H-EarlierProducerGap`; matching caller with zero port bytes and nonzero retail
post-store bytes selects `H-LegitimateZeroThenProducer`. Missing phase markers
make the port arm invalid. Use one build and one run with all controls.
