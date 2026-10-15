# Next work unit

HYPOTHESIS-ID: rt64-opt-frame-limiter

s4908: swap thread is 98% blocked on the VI queue (61 recvs/s, 30 swaps/s); +10 ms/swap sleep absorbed with no rate change. H-guest-O0 refuted for that thread. Remaining: why does the game consume 2 VI messages per swap?

Hypotheses:
- H-retrace-count: game's osViSetEvent retrace_count=2 (events.cpp remaining_retraces) -> one message per 2 VIs by design. But vi_recv=61/s says messages arrive every VI, so retrace_count=1 here: refuted-ish; verify via `[vi-set-event]` log.
- H-game-2wait: the guest frame loop does recv VI twice (frame-skip counter: wait until frame_count >= min_frames); retail does 1 per s4901.
- H-gfx-done-gate: second wait is really a wait on gfx-task-done that arrives late relative to VI.

Discriminator (ONE run, existing log vars): log guest PC / thread id of each VI-queue osRecvMesg (mq 0x80114388) with per-recv timestamp, and swap timestamps; table: recv PCs per swap interval. Same PC twice -> loop-count divider (H-game-2wait, find the counter var and compare to retail via tools/oracle); two PCs -> the second is a gate. Control: s4908 sleep arm already shows counters respond.

Recipe: scratch/agent/run_s4908.sh (binary build/RogueSquadron64Recomp, counters in mesgqueue.cpp s4908_vi_recv).
