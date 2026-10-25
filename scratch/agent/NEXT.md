# NEXT: G1d step 41 - HUD anchor: mark the second (1.6x) store per x coordinate
HYPOTHESIS-ID: g1d-widescreen
s6148 census: 8 HUD blocks at 0x80340240+0x30*n, x@+0x24 y@+0x28, each stored twice in initHudStruct (4:3 value then ~1.6x value; second wins). s6147 mark likely hit the overwritten first store for blocks 6 (x 76->121.6) and 7 (x 106->169.6/177).
Hypotheses: H-layout (first store overwritten; mark the second) vs H-perframe (a writer outside initHudStruct re-sets disc/counter x each frame) vs H-parent.
Discriminator: one run with ROGUESQ_HUD_MARKCLS=x restricted to the LAST store per address (or MARKPC = pcs 0x800c0354,0x800c0530,0x800c0568 etc.) and fb dump; if blocks 6/7 (disc/counter) move -> H-layout, implement ROGUESQ_HUD_ANCHOR (x<160 shifted -(virtW-320)/2*1.6-scale, x>=160 +) in the fixup under ROGUESQ_ASPECT != 4:3. If they still do not move -> H-perframe: census stores to 0x80340240..0x80340430 outside pc 0x800C0084..0x800C1B60 over a longer window.
Recipe template: scratch/agent/s6147_run.sh.
