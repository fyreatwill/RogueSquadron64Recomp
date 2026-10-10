# NEXT: with the s4563 stale-head skip on (default), soak past the teardown and identify the next death site
HYPOTHESIS-ID: m5-audio-destub
Established (s4563): head 0x801499B0 is stale for ~5 synth calls after rs_free(0x80179380); skip removes the +5688 crash (A/B).
Hypotheses: H-next-site-same-class (other walkers of freed audio blocks, e.g. 0x801714D0 voice lattice); H-clean (hangar reached); H-other (unrelated crash).
Discriminating step: re-apply s4561/s4562/s4563 scripts after any regen; run scratch/agent/s4563_skip.sh with sleep 150 -> 400 and read the first [CRASH] pc-symbol in arm A; also examine arm B's viRetraceHandlerThread+9296 crash.
