# Next work unit: M5 - classify dominant stale-save crash sites last-guest-pc 0x8000b650 and 0x80001b08

HYPOTHESIS-ID: m5-audio-destub-sequence

s4231: 6 stale runs (scratch/agent/soak_results/s4230_listwatch/r1..r6) crash at last-guest-pc 0x8000b650 (r1,r2,r5) and 0x80001b08 (r4,r6); allocator-list head==0 NOT reproduced (see PORTING-STATE s4231).
Hypotheses: (a) both are audio-thread derefs of the same corrupted voice/list object; (b) 0x8000b650 is a different idiom (host-side garbage ptr, bus error si_addr=0x380000000 etc.); (c) our probe loads / stub gates fabricate the pointer.
Discriminator: map both PCs to functions (grep symbols), read the faulting instruction and the register source from the run.log CRASH stack; one build adding per-site register dump if needed. Instruments from s4231 stay armed (ROGUESQ_LOG_S4222=1).
