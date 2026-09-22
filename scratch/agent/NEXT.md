# Next work unit: qualify image-stage ordering against the exact consumer

HYPOTHESIS-ID: m5-ai-post-pcm-consumer-order

Session 3717 added the exact consumer queue snapshot. In the valid real-arm
hangar sample, 191 image rows joined to a logged consumer ordinal: stage 2 was
31/96 queue matches and 65 mismatches; stage 3 was 31/95 matches and 64
mismatches. The silent arm stalled at title on the fixed-budget retries, and
the retail oracle was unavailable because its debugger-enabled core is absent.
The result is single-source port evidence for `H-AudioDrainNotConsumed`.

Competing hypotheses:

- `H-AudioDrainNotConsumed`: image-stage sees queue state that differs from the
  exact PCM consumer at the same phase-local ordinal. Selected provisionally
  by 129/191 mismatches, with stage-2 and stage-3 support.
- `H-AudioStageQueueGate`: image-stage depends on a distinct queue threshold or
  drain cadence. A simple consistently-low threshold was rejected at s3716;
  the next run must test ordering rather than add another threshold counter.
- `H-AudioDrainParity`: image-stage and the exact PCM consumer expose matching
  queue state while stage counts still diverge. Refuted in the measured real
  arm, but not independently confirmed against retail.

Discriminator: add a phase-local callback sequence/timestamp to both image-stage
and consumer rows, then classify each mismatch as image-before-consumer,
consumer-before-image, or same-callback-order. A stable image-before-consumer
ordering with mismatched queue snapshots selects a scheduling boundary;
interleaving with no stable order keeps `H-AudioDrainNotConsumed` open. Require
both target origins and the RSP/task controls; do not alter selector, clear,
task, audio route, or payload state.

Exact commands:

`DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp`

`zsh scratch/agent/run_s3436_m5_port_frequency_contract.sh`
