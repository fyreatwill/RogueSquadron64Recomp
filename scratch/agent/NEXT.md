# NEXT: why is the displaced pri-10 allocator (guest tid 3) never re-popped after the VI-readied audio thread preempts it inside rs_malloc?
HYPOTHESIS-ID: m5-audio-destub
Context (s4582): VI retrace message drained at allocator's osRecvMesg readies audio thread (pri 122); allocator never regains control (P#2 never prints, ~30k in-window handoffs among pri 117-122 threads).
Hypotheses: H-starve (allocator sits in running_queue but check_running_queue's strict-greater gate + run_next only on full block means higher threads never fully block); H-lost (allocator dropped from running_queue / state corrupted, e.g. enqueued twice or never re-queued); H-blocked (allocator is actually blocked on a mesgqueue that nothing sends to).
Discriminator (ONE build): in swap_to_thread/run_next_thread/check_running_queue while inflight=1 log the running_queue contents (id,pri,state) and tid-3 state/queue membership every Nth decision (+ first 20 unconditionally as control); also log blocked_queue membership for tid 3. Outcome: tid 3 in running_queue -> H-starve; absent + state BLOCKED -> H-blocked (find the queue); absent + QUEUED -> H-lost.
Recipe: copy scratch/agent/s4582_enq.sh (3 arms, 200 s).
