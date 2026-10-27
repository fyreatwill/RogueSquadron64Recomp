# NEXT: fold s6417_dd_mesh [meshlog] and decide H-farclip (G1c phase 2)
HYPOTHESIS-ID: g1c-dd-phase2
Hypotheses: H-farclip (LOD table 0x8009DE98..A0 / far cutoff DEB4 are dd-independent, so buildGridCellMeshForFace severs the render chain far nodes at dd3); H-vtx (chain intact but per-cell vertex/DL build or tile residency skips far cells); H-ucode (cells emitted, clipped downstream).
Do: read the new SOAK-RESULTS line for s6417_dd_mesh and grep '[meshlog]' in scratch/agent/soak_results/s6417_dd_mesh_*.log (per arm logs under scratch/agent/m6/s6414_attpin).
Outcomes: table identical across d1b/d2/u3 AND chain much smaller than list at u3 (bins >=B4 large) => H-farclip: add tools/apply_* that scales DE98..DEB4 by dd (squared) at the same place apply_s6036_dd scales DEAC, rebuild, rerun same recipe, check terrain returns on position-matched frames. chain~=list => H-vtx/H-ucode: next count terrain RDP tris per cell origin.
Control: d1b/d2 chain vs list must be sane (positive control that the log fires and chain walk works).
