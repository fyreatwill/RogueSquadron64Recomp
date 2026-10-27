# NEXT: who writes cell rec[3]/rec[4] (=0xFE sentinel on rejected dd4 cells) and what caps its footprint?
HYPOTHESIS-ID: g1c-span-reject-predicate

s6525: all 100 dd4 EMPTY returns have c3=c4=-2, plane=127 sentinel (single-source offline).
Hypotheses: H-builder-radius (rec builder loops over a fixed cell count/radius, not scaled by dd), H-reset-sentinel (recs are reset to 0xFE each frame and refilled only for in-footprint cells), H-by-design (far cells legitimately empty).
Discriminator (one build, one run): at the EMPTY return dump 8 raw rec bytes for the first 4 rejecting cells AND the same cells' address; grep recompiled funcs for stores to cell+3/+4 (base 0x80246434, stride 30) to name writer; positive control: a non-rejecting cell dump must show rec3 != -2. If writer loop bound is a constant -> scale it with dd (patch in fixup script); if rec is refilled but window -2 -> by-design.
