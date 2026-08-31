# NEXT work unit — M5 upstream producer edge census

HYPOTHESIS-ID: m5-upstream-producer-edge

Before building, ask the retail oracle for driven, phase-gated rows at
`0x8002BEEC` and `0x800078EC`, with the whole-RDRAM watch as the same-run
positive control. Use Rice and the canonical Start schedule from
`tools/oracle/README.md`; retain predecessor and target-byte fields. Then
build once and run one port census with the existing phase, audio-task,
callback, PCM, and static `rs_memset` controls. Do not change output or audio
behavior.

Competing hypotheses:

- `H-RetailDrivenProducer`: driven retail shows nonzero target writes from
  `0x8002BEEC -> 0x800078EC`; the port still has only the zero-fill path, so
  the missing edge is upstream of the observed port writer.
- `H-PortMatchingProducer`: the port exposes the same caller edge and target
  bytes; the gap is an execution/translation mismatch after the writer.
- `H-LegitimateZeroWriter`: both routes expose the writer edge but write zero;
  the missing producer is later than this store.

Discriminator: a valid driven retail row with nonzero target bytes plus no
matching port edge selects `H-RetailDrivenProducer`; a matching nonzero port
edge selects `H-PortMatchingProducer`; a matching zero edge on both routes
selects `H-LegitimateZeroWriter`. If the retail phase markers or whole-RDRAM
control do not fire, the oracle arm is invalid and no hypothesis is selected.

Exact port route shape:

    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_M5_CALLBACK_WRITER=1 ROGUESQ_LOG_M5_STATIC_CALLS=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a' PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS='3:start 6:start 9:start 12:start 16:a 20:a 24:start 28:a' PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 zsh tools/probe.sh scratch/agent/NEXT-RUN 75 0.5
