# Next: close poison-on-free thread; return to strategic priority (M5 de-stub step per docs/M5-AUDIO-PLAN.md)
HYPOTHESIS-ID: m5-audio-destub
s5060 (poison A/B, 2 arms, positive control fired) found no read-after-free on the mission route. The s5041/s5042 hooks are applied in generated funcs_0.c (inert without ROGUESQ_FREE_POISON/CENSUS); revert with tools/revert_s5041_s5042_hooks.py if they interfere. Next: read the first unexecuted step in docs/M5-AUDIO-PLAN.md, write competing hypotheses + discriminator here, build all arms in one iteration.
