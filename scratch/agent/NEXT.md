# NEXT work unit — M5 exact earlier-producer target attribution

HYPOTHESIS-ID: m5-earlier-producer-contract

The 88 generated `jal 0x800078E0` callsites are now enumerated. Before
building, run the retail oracle with whole-RDRAM control and only the exact
predecessor/writer PCs plus target-span watch; then build once and run the
equivalent port census with the existing phase, audio-task, callback-writer,
PCM, and static-call controls. Do not change output or audio behavior.

Competing hypotheses:

- `H-EarlierPortContract`: retail has a phase-gated target write preceded by
  the selected producer while the port still has only `0x8008F2CC` zero-fill.
- `H-DownstreamPortMismatch`: the port exposes matching caller/input rows with
  nonzero target bytes; the gap is downstream of this boundary.
- `H-LegitimateEarlierZero`: both routes expose the caller/input edge but write
  zero; the zero fill is legitimate here and data is produced later.

Discriminator: a valid retail caller/input row with no port counterpart selects
`H-EarlierPortContract`; matching nonzero port rows select
`H-DownstreamPortMismatch`; matching zero rows on both routes select
`H-LegitimateEarlierZero`. If the retail hangar phase bucket is absent, the
oracle arm is partial and no hangar hypothesis is selected.

Exact oracle route shape:

    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 120 --watch-write 0x0:0x800000 --watch-write 0x1798B0:0x179A48 --watch-pc 0x8002BEE8,0x800078E8,0x800078EC --pc-phase-log-width 0x006AB400:512 --pc-hist-watch 1 --pc-hist-phase 0x006AB400:512 --vi-trace --press '6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start' --hold-ms 150

Expected: whole-RDRAM control and predecessor/writer executions fire. A
phase-gated target write with those predecessors is the retail positive arm;
no target rows despite the control means payload attribution is partial.

Exact port route shape:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_M5_CALLBACK_WRITER=1 ROGUESQ_LOG_M5_STATIC_CALLS=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a' PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS='3:start 6:start 9:start 12:start 16:a 20:a 24:start 28:a' PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 zsh tools/probe.sh scratch/agent/port_s3390 75 0.5
