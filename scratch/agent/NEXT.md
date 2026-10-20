# NEXT (s5658): fold s5657_vsnap_a soak verdict
Read scratch/agent/soak_results/s5657_vsnap_a_*.log, grep '\[vsnap\]'. Wide hash must change (positive control) else null is void.
Outcomes: rails>0 at first vsnap and NARROW never changes => H-P (pre-existing; trace what initialised 1B2C60.. at boot / ROM DMA, then who owns voice slot +0x198 pointer -> H-A). NARROW-CHANGED line w/ rails jump => find the uncovered store form (swl/swr/sdc1/memcpy helpers) around that task.
HYPOTHESIS-ID: g2-voice-never-requested
