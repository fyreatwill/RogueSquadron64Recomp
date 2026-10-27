# Next: why does radfade f=1 not darken terrain? (write-path positive control)
HYPOTHESIS-ID: g3c-owner-visual
s6326: ctl arm (ROGUESQ_EDGE_FADE_R=0,1, f=1 logged) has dark fraction 0.0017 vs nofade 0.0023 -> the fade write at 0x8004B910 epilogue has no visible effect.
Hypotheses: H-combiner (terrain combiner ignores shade RGB: uses texture/env only), H-readback (rdram-readback fbd frames are not what RT64 presents; use present capture), H-order (epilogue write is overwritten/precedes recolour), H-misapplied (applied to non-terrain verts).
Discriminator, one build: env flag forces lit RGB to saturated red at the epilogue for all verts; run 1 arm lvl1 dd3 and check (a) red fraction in rdram fbd, (b) in RT64 present capture. Red in (b) not (a) -> readback; red nowhere -> combiner/order; red on terrain only -> write path OK and fade math (f applied to wrong channel) is the bug.
See tools/apply_s6311_edgefade.py (s6325 block ~line 148-160) for the patch; regen order applies.
