# Next work unit (s4465): reproduce s4462's VI-1024 pool crossing, or retire it

HYPOTHESIS-ID: m5-ai-event-cadence

State (s4464): at VI 640 insert pointers are in per-phase rs_malloc'd 0xF7C tables; no pool overlap; in_pool_range=0 over 4 runs, none reached VI 1024.
Hypotheses: (A) crossing at VI 1024 is real (tables/pool overlap later); (B) it was a tracker artifact of the s4462 recipe (min/max-style or stale alloc view); (C) 1024 phase just not reached by the 120s recipe.
Discriminator: rerun scratch/agent/s4466_run.sh with longer length (arg 120 -> 300) and PROBE_PHASE_TIMEOUT=300 until vi=1024 lines appear; replay with scratch/agent/s4466_an.py extended to report live rs_malloc blocks covering each in_pool_range=1 insert val. A: a live block other than the pool covers val; B: val covered by its own table; C: no vi=1024 -> extend again.
