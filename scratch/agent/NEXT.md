# Next work unit

HYPOTHESIS-ID: guest-2vi-wait

s4911: VI thread has one recv site (60 iter/s). The 30 Hz element is the gfx thread (tid 3): submitGfxFrame 30/s, waitForPostSwapAck (0x8001C260, mq 0x80128CF0) blocks 60/s ~810 ms/s.
Hypotheses: H-design-2ack (waitForPostSwapAck needs 2 retrace acks per frame by the game's frame-pacing variable), H-late-ack (ack/swap message arrives one VI late: sender is waitOnVideoQueue / VI handler send), H-emu-task-slow (emulated SP/DP task completion > 1 retrace so the game legitimately drops to 30).
Discriminator (ONE build): read waitForPostSwapAck generated C (../N64Recomp/RecompiledFuncs/funcs_*.c) first -- what count/variable does it loop on -- then log that variable + sends to mq 0x80128CF0 (sender site via same host-ra trick on osSendMesg_recomp) per second in the 30 Hz stretch. Count var ==2 => design; sends 60/s but loop wants 1 => late ack.
Do not add host timing fields. If this stalls, resume M5 audio plan (docs/M5-AUDIO-PLAN.md).
