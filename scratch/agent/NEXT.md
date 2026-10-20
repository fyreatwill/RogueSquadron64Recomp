# NEXT (s5659): fold s5658_vsnap_b soak verdict
grep '\[vsnap\]' scratch/agent/m6/s5658_vsnap_b/run.log. Now logs only on narrow rail-count change (+every 1000 tasks); wide_hash still present as control.
Outcomes: sudden jump rails 0->~190 at task T => find who wrote at T (uncovered store form: swl/swr/sdc1/memcpy/DMA-in from ROM/PI); gradual => heap reuse by game code, trace allocator owner of 1B2C60; never >0 => hits come from different addr (re-check dump source addr).
HYPOTHESIS-ID: g2-voice-never-requested
