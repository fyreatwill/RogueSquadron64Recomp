# Next work unit

HYPOTHESIS-ID: guest-2vi-wait

s4917: H-ordering refuted. Port's bufferArbiterProducerMark (gfx thread) stores slot state 3 (pc 0x8001BDFC) before 2,414/2,419 two-recv waits, state 4 (0x8001BE30) before 694/705 one-recv waits. Branch logic (funcs_5.c ~5961-6136): slot in state 2 -> commit 4 if no other slot is 4 AND no state-5 slot passes the counter test lbu(0x80128EAA) < lbu(0x80128EAB)-1 ... else park at 3.
Hypotheses: H-5-not-retired (prior frame's slot still state 5 at commit because the handler's 5->0 retire runs after the gfx thread's next commit; i.e. gfx thread runs ahead of retrace), H-counter (byte +0/+1 values differ so the test fails; a counter is initialised/updated by something we stub), H-state-4-elsewhere (another slot is 4 at commit).
ONE build, one run: extend rs64_s4916_sb-style mark at BD90 (state-4 found), BDDC (state-5 found) and the BDF4 compare with the values of bytes +0,+1 and all 8 slot bytes at producerMark entry; also log t of each handler 5->0 store (pc 0x800199A4/DC) vs producer entry per frame. Run with ROGUESQ_S4913_MAX=400000 (essential; 12k cap hides the two-recv regime), sleep 100.
Outcome: slot 5 present at commit in all two-recv frames with retire after => port gfx thread leads the VI handler by a retrace (look at what releases the gfx thread: waitOnVideoQueue/osViSwapBuffer timing); counter differs => trace the counter writer.
If stalled, resume the M5 audio plan.
