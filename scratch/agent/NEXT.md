# NEXT work unit — M5 upstream predecessor census

HYPOTHESIS-ID: m5-producer-predecessor-edge

Before building, ask the retail oracle for driven, phase-gated execution rows
at `0x800078E0` and `0x8002BEE8`, retaining predecessor, arguments, and
target-span bytes, with the whole-RDRAM positive control in the same run. Use
Rice and the canonical Start schedule. Then build once and run one port census
with the existing phase, audio-task, callback-writer, PCM, and static-call
controls. Do not change output or audio behavior.

Competing hypotheses:

- `H-EarlierRetailProducer`: valid like-for-like retail hangar predecessor
  rows are nonzero while the port still has only `0x8008F2CC` zero-fill; the
  gap is earlier than the observed port writer.
- `H-PortPredecessorMatch`: the port exposes the same predecessor edge with
  nonzero target bytes; the gap is a translation/dispatch mismatch after it.
- `H-LegitimateZeroBoundary`: both routes expose the predecessor edge but
  write zero; the zero fill is legitimate here and data is produced later.

Discriminator: valid retail hangar predecessor rows plus no matching port edge
select `H-EarlierRetailProducer`; matching nonzero port rows select
`H-PortPredecessorMatch`; matching zero rows on both routes select
`H-LegitimateZeroBoundary`. If the retail hangar phase bucket is absent, the
oracle arm is partial and no hangar hypothesis is selected.

Exact port route shape:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_M5_CALLBACK_WRITER=1 ROGUESQ_LOG_M5_STATIC_CALLS=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a' PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS='3:start 6:start 9:start 12:start 16:a 20:a 24:start 28:a' PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 zsh tools/probe.sh scratch/agent/port_s3390 75 0.5
