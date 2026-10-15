# Next work unit

HYPOTHESIS-ID: guest-2vi-wait

s4912: waitForPostSwapAck loops recv(mq 0x80128CF0)+yield until byte 0x8011A8C8==0; only advanceVideoFrame clears it (clearPostSwapPendingFlags) AFTER signalFrameSyncMesgNonblock/swap/waitOnVideoQueue. Recvs/call flipped 1->2 mid-run (s4912 log).
Hypotheses: H-late-ack (sync msg wakes gfx thread before flag clear -> needs next VI), H-emu-task-slow (frame work exceeds a retrace after the transition), H-transition-state (a game state change at the flip alters ordering).
ONE build, one run: per frame log ordinals/host-ns of: signalFrameSyncMesgNonblock, waitOnVideoQueue return, clearPostSwapPendingFlags, gfx-thread recv wake + flag A at wake; plus VI count marker (phase-gated, PROBE_PHASE_WIDTH) across the 1->2 flip. Positive control: log must show flag A==1 at some wake. Outcome: A==1 at first wake in 2-recv frames and 0 in 1-recv frames => late-ack; what differs in timing before the flip selects emu-slow vs state.
Do not add more single fields afterwards; if stalled, resume M5 audio plan.
