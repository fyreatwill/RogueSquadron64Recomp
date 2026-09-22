# Next work unit: join image-stage queue state to exact PCM consumer

HYPOTHESIS-ID: m5-ai-post-pcm-consumer

Session 3716 added `[m5-image-queue]` rows. In valid hangar origin
`0x006AB400`, real audio had 190 image-stage rows (95 stage-2 and 95 stage-3)
with queue depth 0–4581 bytes; the first row saw 3045 bytes and four PCM
consumers already seen. Silent reached hangar and passed its RSP control but,
as the intentional stub arm, had no image-stage rows. This rejects a simple
consistently-low/drained image-stage queue gate and remains single-source port
evidence.

Competing hypotheses:

- `H-AudioDrainNotConsumed`: image-stage sees queue state that differs from the
  exact PCM consumer at the same phase-local ordinal.
- `H-AudioStageQueueGate`: image-stage depends on a distinct queue threshold or
  drain cadence. A simple consistently-low threshold was rejected at s3716.
- `H-AudioDrainParity`: image-stage and the exact PCM consumer expose matching
  queue state while stage counts still diverge.

Discriminator: add the exact phase-local consumer ordinal and queue snapshot to
each `[pcm-boundary-consumer]` row, then join it to the image-stage
`pcm_consumers_seen` value by arm, phase, and ordinal. A mismatch between the
image-stage snapshot and the exact consumer snapshot selects
`H-AudioDrainNotConsumed`; matching snapshots with stage divergence selects
`H-AudioDrainParity`. The existing RSP controls must fire in both arms. Do not
alter selector, clear, task, audio route, or payload state.

Exact commands:

`DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp`

`zsh scratch/agent/run_s3436_m5_port_frequency_contract.sh`
