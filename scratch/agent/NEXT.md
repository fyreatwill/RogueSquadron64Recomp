# NEXT: A/B the s659 reason (thr11d fs stall) with ROGUESQ_FL_HDR_HARD_SKIP=1; decide wild-width writeback policy

HYPOTHESIS-ID: wild-setcimg-writeback

s4546: the sample-heap wipe + VI-640 fillSampleStreamRange death are the RT64 ALLOW_WILD_FL writeback of the garbage SETCIMG addr=0x130393 w=1033 siz=3 (range [0x1A742B,0x28633F)). HARD_SKIP=1 survives 3/3 to 180 s; default 1/3 survives (the one that never fired ALLOW_WILD_FL).

Hypotheses: H-allow-needed (s659's thr11d stall returns with HARD_SKIP), H-allow-unneeded (stall was a different cause; HARD_SKIP is safe), H-restore-range (restoring the whole covered range instead of 16 B fixes both).
Discriminating measurement: the s659 thr11d recipe (grep PORTING-STATE.md "## Session 659" and "thr11d" for its exact env/keys) run 3x default vs 3x HARD_SKIP=1 in this build, interleaved; verdict on whether the post-exit fs stall appears. Positive control: default arm reproduces the stall (or the ALLOW_WILD_FL line) in the same batch.
Then: if H-allow-unneeded, make a restore-or-skip decision with an ORIGIN line; separately start on who sets the SETCIMG (s4531).
