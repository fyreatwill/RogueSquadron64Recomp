# Next work unit: join host queue state to image-stage

HYPOTHESIS-ID: m5-ai-post-pcm-consumer

Session 3715 added `[m5-audio-host]` rows. In hangar origin `0x006AB400`,
real audio had 79 queue/78 remaining rows, depth 0–4581 bytes, and 58/79
negative inter-sample deltas; silent had 16/16, depth 0–3813, and 8/16.
Both arms passed 1,024 RSP-source controls; real had 5,060 image-stage rows,
silent zero. This is single-source port evidence. The oracle positive control
fired but its attempt did not reach target hangar, so it adds no retail queue
observation.

Competing hypotheses:

- `H-AudioDrainNotConsumed`: image-stage sees buffered/low queue state that is
  not the same state as the PCM consumer, so the host queue divergence is not
  the stage discriminator.
- `H-AudioStageQueueGate`: image-stage is reached only after a distinct queue
  threshold or drain cadence, explaining real-versus-silent stage divergence.
- `H-AudioDrainParity`: at the image-stage event, both arms expose matching
  queue state despite different producer-side cadence; the unresolved boundary
  is downstream of the host queue.

Discriminator: add one phase-gated host queue-depth snapshot at each
`audtask-image-stage` event and join it to the first `[pcm-boundary-consumer]`
row by arm-local phase/ordinal. A consistent low/drained queue only on real
audio selects `H-AudioStageQueueGate`; matching image-stage queue state with
different image-stage counts selects `H-AudioDrainNotConsumed` or
`H-AudioDrainParity` according to the consumer join. Keep both arms and the
existing RSP controls in one build/run. Do not alter selector, clear, task,
audio route, or payload state.

Exact commands:

`DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp`

`zsh scratch/agent/run_s3436_m5_port_frequency_contract.sh`
