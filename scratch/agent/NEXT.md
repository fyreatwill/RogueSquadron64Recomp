# NEXT: does EMPTY fall monotonically to the dd1 level as ROGUESQ_SPANSCALE grows (and does the frame improve)?
HYPOTHESIS-ID: g1c-span-reject-predicate

s6523: consumer decoded (skip if A==B==-128; reject if A<rec[3] or rec[4]<B; signed lb). dd4 EMPTY 24% (s1) -> 14% (s4); dd1 0.2%.
Hypotheses: H-scale (byte range is the limit: EMPTY keeps falling toward 0.2% at s=8/16), H-reject-by-design (plateau near 14%: remaining rejects are real rec-window rejects of far terrain), H-phase-confound (differences are key/phase sampling; compare EMPTY only within matched key ranges).
Discriminator: copy scratch/agent/s6523_spanscale.sh; arms dd4 s4 / s8 / s16 (tools/apply_s6523_spanscale.py already built in; no rebuild needed) and compute EMPTY fraction per key window 745+ (mission table) only. Also save a framebuffer per arm (fixed pose via POSE_REF) and run the terrain-fraction scorer. Monotone->0 + more terrain pixels = H-scale: bake dd-derived scale into ROGUESQ_DRAW_DISTANCE. Plateau = H-reject-by-design.
