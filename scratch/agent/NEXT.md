# Next work unit

HYPOTHESIS-ID: guest-2vi-wait

s4910: at -O2 RT64 (default) swaps stay 30/s; host-slow refuted. Leading: the guest waits 2 retraces per swap (design) or a gate stays closed one VI.
Hypotheses: H-design-30fps (guest osViSetSwapBuffer-style wait of 2 VIs; same in retail oracle? retail steady at 1 origin change per retrace per s4900/s4901 so likely NOT design), H-gfx-done-gate (guest waits on a gfx-done msg that arrives one VI late), H-viqueue-msg-count (a message consumed by the first recv is counted twice).
Discriminator: log guest return address (thread-local guest PC) at the two VI-queue recvs per swap by tid 0, ONE build, plus the gfx-done msg timestamp relative to the retraces. Same call site twice => counter/loop in guest; different sites => gate.
Do not add more host-side timing fields. If this stalls, resume M5 audio plan (docs/M5-AUDIO-PLAN.md).
