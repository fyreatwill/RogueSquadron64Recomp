# NEXT: which thread runs musyxMixActiveVoices inside the allocateSongChannelArray window, and is the guest holding an interrupt mask/lock there?
HYPOTHESIS-ID: m5-audio-destub
Context (s4578): count 0x80149700 is stored (sh 0x8008F0CC) BEFORE rs_malloc(0x8008F0D0); base 0x801496FC/F8 stored AFTER (0x8008F0E4/EC). The 6th alloc (count 32) never completes (no 6th [s4542-alloc]); the mixer then runs with count 32 + stale 18-slot base -> bad voice. Host writes and misread refuted. Do not re-poll the count.
Hypotheses:
 H-preempt: the mixer is a different host thread/guest thread that our scheduler lets run while the alloc thread is inside rs_malloc; retail masks interrupts or the thread priorities forbid it. Predicted: thread id at sh-time != thread id at bad mix call, and osSetIntMask/ lock state at sh time says "masked" in guest code that we ignore.
 H-same-thread-reentry: rs_malloc itself (or an audio callback inside it) calls the mixer on the same thread. Predicted: same thread id, mix call appears nested under the alloc (call depth/ra chain).
 H-malloc-hang: rs_malloc(0x1100) blocks/loops and the mixer is just another normal thread; then retail allocator would succeed -> inspect rs_malloc freelist for the 0x1100 request.
Discriminator (ONE build, extend tools/apply_s4578 or new apply_s4579): at allocateSongChannelArray sh (pre-rs_malloc) and at rs_malloc return, and at every musyxMixActiveVoices entry once count>18, print host thread id, guest osGetThreadId/current thread ptr, interrupt-mask state, and an in-alloc flag; positive control: alloc #1..#5 print matched pre/post pairs.
Outcomes: tid differs + in-alloc flag set at mix -> H-preempt (then find retail's protection: osSetIntMask/ hwDisableIrq in the caller of 0x8008F0A0); same tid nested -> H-same-thread-reentry; no mix while in-alloc but rs_malloc never returns -> H-malloc-hang.
Recipe: copy scratch/agent/s4578_poll.sh.
