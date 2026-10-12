# NEXT: decide whether the hangar white pillar stubs are a defect
HYPOTHESIS-ID: hangar-renderer-artifacts

s4644: rim band + holo spikes not visible in current frames; residual = white vertical stubs at x~200/430/865/1085/1130 (f_003 of scratch/agent/s4642_viext).
Hypotheses: H-design (retail lights these pillar edges white), H-tex (a texture/combiner on pillar edge tris is wrong in RT64), H-shade (leftover vertex shade/clamp difference).
Discriminator: need a retail pixel reference. Find a retail hangar screenshot (external, e.g. any emulator capture of "Available Craft" screen) and compare; or dump the RDP triangles covering x~430 (RT64 tri-index mask tools from s4635) and read their combiner/shade values.
If H-design is confirmed, close the hangar-artifact thread and fall to M5/M3 items (Next steps 2-5). Do not start the rename sweep while the engineering-change gate is near 6.
