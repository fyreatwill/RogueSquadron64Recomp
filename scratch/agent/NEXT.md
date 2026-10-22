# NEXT (s5928): consume the human lv0 play result (BLOCKED physical)

HYPOTHESIS-ID: g1-human-play-outcome

If scratch/agent/m6/*/summary from g1_human_play.sh exists: win -> mark G1 tooling-limit, take G3 (hangar framebuffer diff, ROGUESQ_FB_DUMP_DIR works at VI_WIDTH); lose/softlock/crash -> trace from [ctr1]/[mend]/[plpos] in run.log, name the writer.
If none exists: the unblock tier should take G3 and LAND a runtime change (not an observation).
