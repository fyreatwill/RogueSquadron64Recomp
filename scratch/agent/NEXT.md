# Next work unit (s4462): SND-pointer vs audio-node-pool overlap

HYPOTHESIS-ID: m5-ai-event-cadence

State (s4461): 0x800853A8 is the shift loop in factor5SortedTableInsertWidePair; 0x80193C18 is a caller-supplied relocateSndPointer value (a1), first stored at pc 0x80085424. Not a corruption writer.
Hypotheses: (F) registered SND ptr C18 points into memory later reused as audio node pool (overlap/freed buffer); (E) SND data legitimately there, pool mis-placed; (G) C18 is a benign base offset (pool_base-8 style) never dereferenced as a node.
Discriminator: one run (reuse s4459_run.sh pattern) with a hook at entry of factor5SortedTableInsertWidePair logging a0,a1,a2,ra per call (VI-tagged), plus the ranges handed out by the allocator for the pool (0x8008F708) and the SND section base used by relocateSndPointer. Control: call count>0 and a1==C18 appears. F: pool range contains C18 while SND base range does not own it; E: SND range contains C18 and pool overlaps it; G: a1 is not in any range / never read.
