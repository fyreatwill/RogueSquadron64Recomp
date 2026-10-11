# NEXT: why does tid 3 (allocator) starve in the rs_malloc window if Ai rate is legit (1/VI)? Measure per-thread run time/handoff count per VI frame inside the window.
HYPOTHESIS-ID: m5-audio-destub
Context (s4585): Ai enqueue = 1.00/VI, no guest self-sends. H-inflated/H-selfsend refuted. Remaining: H-handler-cost (audio handler runs long per Ai msg), H-hostblock (tid 3 waits on something host-side, e.g. a Pi/DMA message never delivered), H-sched (non-preemptive scheduler lets pri 117-122 threads cycle on Sp/Si msgs, d_si=0.82/VI).
Discriminator (ONE build): in the s4581 window log per-VI: time and switch count by thread id, and the queue addr tid 3 is blocked on at each Vi. Control: same table outside the window. Recipe: copy scratch/agent/s4585_rq.sh.
