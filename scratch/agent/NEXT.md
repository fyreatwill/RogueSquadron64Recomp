# NEXT: where do the drawn TriGen terrain heights diverge from the camera collision's height data? (s7113: H-raymiss confirmed)
HYPOTHESIS-ID: fps60-wall-lod
Context: s7113 (tools/s7113_raymiss.py, offline on the s7112 capture) rebuilt the eye-cell TRI_GEN tris in world space (cross-pose
static control |dy| 0.0017 / |dxz| 0.0043 median) and showed the camera's ray test (sampleTerrainAtNpcPosition, s7103 exit mask)
misses the drawn wall on 74% of rays whose corner sits 25-50% f20 inside it, and the y-clamp sampler 0x80067D90 under the camera
matches the drawn height within 0.01 on only 9% of ticks (loss ticks: drawn ground 0.08-0.25 ABOVE the game floor, y-down world).
Drawn vertices sit 0.042 (p50) off the 0.5 lattice. Geomorph (H-morph) not supported offline (|dy| does not grow with depth change).
Hypotheses (one instrument, one build, one run):
 H-coarse  the collision reads a different / coarser height source (terrain struct 0x80138058) than the TriGen cell source heights.
 H-ponder  TriGen input heights equal the collision data at lattice nodes, but the ucode (or CPU cell builder) displaces the drawn
           vertices (ponderation / edge-correction / option bits) so the drawn surface leaves the collision surface.
 H-interp  same node heights, different interpolation inside the cell (collision bilinear/other diagonal vs drawn 4x4 sub-quads).
Discriminator: per flight tick, for the eye cell's 5x5 lattice nodes, log (a) the collision height (call 0x80067D90 vertically at each
node xz on a scratch stack, as s7103 does for sampleTerrainAtNpcPosition) and (b) the TriGen INPUT vertex data the CPU builder hands
the ucode for that cell (S7105_EMIT / buildGridCellMeshForFace source words). Offline join with the s7112 rebuilt drawn vertices.
 (a)!=(b) at nodes -> H-coarse; (a)==(b) at nodes but drawn != (b) -> H-ponder (name the ucode/CPU step); nodes equal and drawn
 equal at nodes but mid-quad differs -> H-interp. Positive control: on flat flight cells (low slope) all three must agree.
Fix direction once named (opt-in, default retail): make the camera push-out / y-clamp test the drawn surface (e.g. sample the
drawn cell's height for the y clamp, or add a margin equal to the measured max displacement), qualified by losscan eye-cell losses.
Run recipe: scratch/s7112/arm.zsh 6 4 <name> "<s7112 env + new env>" 120 260; analysis tools/s7113_raymiss.py tri.bin push.txt tris.bin losscan.txt.
