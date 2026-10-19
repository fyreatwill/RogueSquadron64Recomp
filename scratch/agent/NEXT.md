Single next work unit: read the s5580_plume_lle4 verdict (SOAK-RESULTS.md tail + scratch/agent/soak_results/s5580_plume_lle4/summary), fold into ledger. FIRST check it is not a null: duration must be >100 s and summary must contain run-N last-origin lines with real origins.

H1: titles>=2/4 -> write an lldb variant of the recipe (see done/s5463_plume_title8_a_*.sh for the lldb attach pattern) and queue it; loop until si_addr=0x58 recurs.
H2: titles=0/4 with last-origin 0x696100 -> regression in title route since s5463; diff env sets against s5463 recipe.
H3: titles reached, no crash -> raise N to 8 (two queue entries, 600 s cap).
Discriminator: per-attempt TITLE count with the LLE trio.
Recipe hygiene: line 2 of every recipe = zsh re-exec guard.

HYPOTHESIS-ID: m6-title-plume-lldb
