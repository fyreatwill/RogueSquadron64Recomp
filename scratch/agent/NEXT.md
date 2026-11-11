# NEXT: is the camera collision surface the same surface the eye-cell TriGen mesh renders? (s7112: ucode drop refuted)
HYPOTHESIS-ID: fps60-wall-raymiss
Context: s7112 (ROGUESQ_S7112_TRI + tools/s7112_trireject.py) showed the F5 ucode emits the visible eye-cell tris on loss swaps;
the near cut is correct clipping, so the rendered wall really lies inside near 15 of the eye. s7111 showed all 4 push-out corner
rays (2*near long) clear at those ticks. So the probe (sampleTerrainAtNpcPosition / push-out at camera 0x80138458) and the render
disagree about where the wall is.
Hypotheses:
 H-lod      the collision samples a coarser height grid / other LOD than the TriGen mesh draws (TriGen ponderation / option edge
            corrections move vertices; walls are steep so a small grid offset is a large horizontal shift).
 H-gap      the rays pass between samples (the 4 corners miss a ridge/wall face that the camera's view frustum crosses in front).
 H-space    a units/space mismatch (render scale vs collision scale, or the dd>1 extended-cell transform) puts the drawn wall off
            the sampled one.
Unit (offline first, capture once): S7112 records already hold clip-space verts of every eye-cell tri per swap. Add to the same
build the camera view matrix per swap (or eye pos + basis from the CHASE log) and invert clip -> world for the eye cell's tris;
compare the world wall plane with the height samples the push-out reads at the 4 corners (CHASE log values) on the 41 loss
swaps vs +-3 s shifted controls. Outcome: drawn surface within near of the eye where the sampled height says clear, offset
consistently along one axis -> H-lod/H-space (measure the offset); offset random and the miss always between corners -> H-gap.
Positive control: on non-loss flight ticks the inverted render surface must match the sampled height within a few units.
Run recipe: scratch/s7112/arm.zsh 6 4 <name> "<s7112 env>" 120 260 (env list in PORTING-STATE s7112).
