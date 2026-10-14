# Correlate the post-swap acknowledgement queue at a live VI-640 stall

HYPOTHESIS-ID: vi640-postswap-ack-queue

(s4798 was a maintenance iteration: CURRENT-TRUTH compacted 730 -> 174 lines, no
experiment run. This unit is carried forward unchanged from s4797.)

The corrected s4797 witness selected the presentation-side explanation: the
Gfx thread remained active in RT64 display-list/update-screen work, while guest
MAIN waited in `submitGfxFrame -> waitForPostSwapAck`; `vi-fs stalled=1` is not
an audio-main wait. The next unit is one queue-counter correlation, with no
runtime mitigation.

Competing hypotheses and discriminator:
- H1: post-swap acknowledgements are never produced because the producer-side
  frame-pair path is blocked. The ack queue's send/deliver counters stop while
  MAIN's receive remains blocked.
- H2: acknowledgements are produced but not delivered to MAIN because the
  cooperative scheduler or queue handoff is blocked. Send/external counters
  advance while the MAIN receive/deliver side does not.
- H3: the observed wait is an intentional frame-pair drop with no pending ack;
  queue counters remain quiet while the Gfx thread continues update-screen
  processing and `vi-fs` keeps reporting `pair=0`.

The discriminating measurement is one run that reaches `vi-fs stalled=1` in
VI 640, then captures the existing `mqdiag` snapshot(s) and one process sample
at that state. H1/H2/H3 are split by the queue's send, delivered, blocked,
external, and requeued deltas; the Gfx-thread and MAIN stacks are controls for
the state gate. A run that lacks the sample positive control or never reaches
the stalled state is route-invalid. The stall is nondeterministic (s4794: 2/5
runs), so plan up to 5 gated attempts in one script and keep the ones that stall.

Commands: use the established s4797 launch environment from `build/` (see the
s4793/s4794 sampler under `scratch/agent/soak_results/s4793/` and its recipe in
`scratch/agent/soak_queue/done/`), arm the existing mqdiag watchdog and passive
breadcrumbs, wait on the log condition `vi-fs stalled=1` rather than a
stopwatch, run `sample <pid>` once the state has persisted for 10 seconds, copy
the matching `mqdiag_NNN.txt` snapshots to `scratch/agent/soak_results/`, then
SIGKILL the game and process group. Do not build or change queue/presentation
behavior before this witness. Avoid zsh nested parameter expansion (it caused
the s4793 false pass).

Expected outcomes: send/deliver frozen -> H1; send/external advancing with
receive blocked -> H2; counters quiet with Gfx still updating -> H3.
