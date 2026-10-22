# NEXT (s5929): oracle same-autopilot differential for G1, else G3 with a landed change

HYPOTHESIS-ID: g1-oracle-same-autopilot-differential

1. Check (static, 10 min) whether the retail oracle accepts the same scripted lv0 input (see run_s3746_oracle_exact_route.sh, g1_fly.sh). If yes: one oracle run with the IDENTICAL schedule, positive control = oracle reaches lv0 flight; compare ctr1/class-1 kill count and mission end vs the port. Oracle also never kills class-1 => G1 is an autopilot limit, close it. Oracle kills many => real port defect with a same-input discriminator.
2. If the oracle cannot take the input: take G3 (hangar framebuffer diff vs oracle, ROGUESQ_FB_DUMP_DIR works at VI_WIDTH) and LAND a runtime/tool change, not an observation.
Open human dependency (not blocking): scratch/agent/g1_human_play.sh human1; if scratch/agent/m6/human1/summary appears, consume it first.
