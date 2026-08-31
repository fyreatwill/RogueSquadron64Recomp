# NEXT work unit — M5 lower-noise target attribution

HYPOTHESIS-ID: m5-earlier-producer-contract

The s3392 oracle arm again passed whole-RDRAM and predecessor execution
controls but emitted no recognizable target-span rows. The first port arm
crashed pre-title in `filterVoiceSampleBlock`; a same-build retry reached
title/hangar and reproduced the port zero-fill row. Before building, run a
lower-noise retail oracle with whole-RDRAM control, the exact target-span
watch, and only `0x800078E8,0x800078EC` execution watches. Then build once
and run the equivalent port census with the existing phase, audio-task,
callback-writer, PCM, and static-call controls. Do not change output or audio
behavior.

Competing hypotheses:

- `H-EarlierPortContract`: retail has a phase-gated target write with the
  selected predecessor while the port still has only `0x8008F2CC` zero-fill.
- `H-DownstreamPortMismatch`: the port exposes a matching nonzero target row;
  the gap is downstream of this boundary.
- `H-LegitimateEarlierZero`: both routes expose the target row with zero;
  this boundary is legitimate and data is produced later.

Discriminator: a target-span row with a valid retail predecessor and no port
counterpart selects `H-EarlierPortContract`; a matching nonzero port row
selects `H-DownstreamPortMismatch`; matching zero rows select
`H-LegitimateEarlierZero`. If the target watch is absent while whole-RDRAM
fires, record the oracle arm as partial and stop repeating this exact census.

Exact oracle route shape:

    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 120 --watch-write 0x0:0x800000 --watch-write 0x1798B0:0x179A48 --watch-pc 0x800078E8,0x800078EC --pc-phase-log-width 0x006AB400:512 --pc-hist-watch 1 --pc-hist-phase 0x006AB400:512 --vi-trace --press '6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start' --hold-ms 150

Expected: whole-RDRAM control and predecessor/writer executions fire. A
phase-gated target write with those predecessors is the retail positive arm;
no target rows despite the control means payload attribution is partial.

Exact port route shape:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_M5_CALLBACK_WRITER=1 ROGUESQ_LOG_M5_STATIC_CALLS=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a' PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS='3:start 6:start 9:start 12:start 16:a 20:a 24:start 28:a' PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 zsh tools/probe.sh scratch/agent/port_s3390 75 0.5
