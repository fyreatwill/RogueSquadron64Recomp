# NEXT: is the Ai-source message rate to queue 0x80149670 (audio thread, pri 122) per VI frame inflated by our AI drain, vs retail's ~1-2/frame?
HYPOTHESIS-ID: m5-audio-destub
Context (s4584): high threads genuinely block on mesgqueues (H-poll refuted); audio thread re-blocks on Ai ~6000 times per 10000 in-window pops, starving tid 3 (allocator).
Hypotheses: H-inflated (our AI drain/enqueue_external_message_src(Ai) fires far faster than retail cadence); H-legit-rate (rate matches retail ~ per VI, starvation arises from handler cost); H-selfsend (the Ai queue is also fed by guest osSendMesg).
Discriminator (ONE build): in enqueue_external_message_src count per-source enqueues per VI-frame bucket during the s4581 window, plus guest osSendMesg counts to 0x80149670; control = first 20 enqueues outside the window. Compare to ~1-2 Ai/frame. Recipe: copy scratch/agent/s4584_rq.sh.
