# NEXT work unit — M5 producer-family predecessor census

HYPOTHESIS-ID: m5-producer-family-predecessor

Before building, ask the retail oracle for driven, phase-gated rows at
`0x80007670` and `0x800078EC`, with the whole-RDRAM watch as the same-run
positive control. Use Rice and the canonical Start schedule from
`tools/oracle/README.md`; retain predecessor and target-byte fields. Then
build once and run one port census with the existing phase, audio-task,
callback-writer, PCM, and static-call controls. Do not change output or audio
behavior.

Competing hypotheses:

- `H-RetailFamilyInput`: retail shows nonzero target writes from the
  `0x80007670`/`0x800078EC` family while the port still has only the
  `0x8008F2CC` zero-fill; the missing edge is upstream of the observed port
  writer.
- `H-PortMatchingFamily`: the port exposes the same producer family and
  target bytes; the gap is an execution/translation mismatch after the
  producer.
- `H-LegitimateZeroBoundary`: both routes expose the producer family but
  write zero; the zero fill is legitimate at this boundary and the missing
  data is later.

Discriminator: valid driven retail rows with nonzero target bytes plus no
matching port producer edge select `H-RetailFamilyInput`; a matching nonzero
port edge selects `H-PortMatchingFamily`; matching zero producer rows on both
routes select `H-LegitimateZeroBoundary`. If the retail phase markers or
whole-RDRAM control do not fire, the oracle arm is invalid and no hypothesis
is selected.

Exact port route shape:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_M5_CALLBACK_WRITER=1 ROGUESQ_LOG_M5_STATIC_CALLS=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a' PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS='3:start 6:start 9:start 12:start 16:a 20:a 24:start 28:a' PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 zsh tools/probe.sh scratch/agent/port_s3388 75 0.5
