# Next work unit: WRAP_FLUSH A/B that actually reaches the hangar (s4275)

HYPOTHESIS-ID: m5-audio-destub-sequence

s4274: s4273_ab.sh at 75 s did not reach VI 512 in either arm. Its autopilot is wrong for this goal.
Hypotheses: W1 flush fixes real loss; W2 flush duplicates draws; W3 neutral.
Discriminator: use the s1949 recipe (scratch/agent/soak_queue/done/s1949_menu_input_yield.sh) for ROGUESQ_AUTOPILOT, run both arms, count odd/sane only after the vi_width=512 phase line, dump frames per arm. Positive control: wrapBumps>0 arm0, flushes>0 arm1.
