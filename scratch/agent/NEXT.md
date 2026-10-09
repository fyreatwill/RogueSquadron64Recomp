# Next work unit (s4318): qualify M5 Step 9 ground-truth boundary

HYPOTHESIS-ID: m5-step9-mort-boundary

State (s4317): the retail/port consumer comparison is fully qualified. Both
arms passed their route controls and supplied 16,384 hangar-gated rows; the
first tuple diverges, selecting a retail/port layout-or-filter difference.
No writer or mitigation is named. The oracle cap change is in
`tools/oracle/rs64_oracle.c` and is bounded diagnostic infrastructure.

Competing hypotheses:

- H-MORT: any remaining audio gap is owned by the CPU-side MORT descriptor/
  decode/output path.
- H-AI: MORT and guest PCM source are valid, but the AI/SDL source-to-consumer
  representation or queue boundary is wrong.
- H-route: neither boundary is implicated; the complete task/voice matrix is
  still absent or the observed issue is route/consumer state elsewhere.

Discriminator: run one phase-gated M5 matrix containing the existing
`audtask-dispatch`, task/DMA, service/status/slot, voice/reap, MORT descriptor,
PCM-source, PCM-consumer, and route controls in both the default image and
`ROGUESQ_AUDIO_UCODE=0` arms. Require whole-RDRAM positive control, title
`1024 @ 0x00790400`, hangar `512 @ 0x006AB400`, and nonzero source PCM. A
MORT descriptor/output mismatch with valid source selects H-MORT; matching
MORT/source with consumer or byte-count divergence selects H-AI; missing
matrix controls or route phase leaves H-route unevaluable. Do not change a
decoder or AI bridge in this unit.

Exact preparation/checks:

`rg -n "audtask-|pcm-|MORT|ROGUESQ_AUDIO_UCODE|PROBE_PHASE_WIDTH" src lib tools scratch/agent | head -200`

Then use the existing validated port driver from `scratch/agent/` with both
audio env arms in one build/run, phase-gated on VI transitions. Record the
complete row in a new bounded scratch result; do not add a diagnostic field or
mitigation until the discriminator is present.
