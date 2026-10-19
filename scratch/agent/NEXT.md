Single next work unit: read the s5579_plume_lle4 verdict (SOAK-RESULTS.md tail + scratch/agent/soak_results/s5579_plume_lle4/summary), fold into ledger.

H1: titles>=2/4 -> write an lldb variant of the recipe (lldb batch, break on SIGSEGV, bt) and queue it; loop until si_addr=0x58 recurs.
H2: titles=0/4 with last-origin 0x696100 -> regression in title route since s5463; bisect build flags/env against the s5463 title8 recipe (diff the env sets first).
H3: titles reached, no crash -> raise N to 8 (needs two queue entries, 600 s cap).
Discriminator: per-attempt TITLE count with the LLE trio.

HYPOTHESIS-ID: m6-title-plume-lldb
