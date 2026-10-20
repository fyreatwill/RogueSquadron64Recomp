# NEXT (s5685): closed-loop altitude hold
Hypotheses: H1 sy drives altitude (s5684: yes, ~0.12-0.19/poll); H2 a sy-feedback autopilot keeps the ship clear of terrain through a 10 min hold; H3 crash/stall is unrelated to altitude.
Discriminator: add an autopilot rule reading ship pos y (pd2 source) and pulsing sy toward a target; compare alive_at_end/vi_stalls over >=3 runs vs the s5678 recipe.
HYPOTHESIS-ID: g1-mission-progression
