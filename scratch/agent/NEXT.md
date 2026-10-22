# NEXT (s5922): where do player bolts spawn relative to class-1 centres, and what gates msg5?

HYPOTHESIS-ID: g1-mission-progression

s5921: tmsg2 refuted as proximity (1.17 vs 1.05/window, no k dependence). Range alone does not step msg5.
Hypotheses: (A) msg5 needs a player bolt/collision object overlapping a class-1 sphere (bolt pos, not ship pos); (B) msg5 needs a state flag (e.g. wave/target-armed) set elsewhere; (C) msg5 only on kill of a linked entity.
Discriminator: one instrument logging player-bolt world pos at spawn and class-1 centres each poll, in one run; report min bolt-to-centre distance vs r<=0.68, plus msg5 deltas. Positive control: poke a bolt pos onto a centre if feasible; else tmsg3/4 parse.
Outcome A-near -> collision radius/bolt path bug; A-far -> bolts never reach (aim/track); B/C -> read msg5 sender in recompiled class-1 fn.
