# NEXT: terrain-window side edge at 21:9 dd4 (G5e residual after s7007)
HYPOTHESIS-ID: dd-side-edge-219
Context: s7007 showed the far fog-colour slab is removed by opt-in DD_MELT. Left over (single-source): an UNFOGGED straight edge with a corner at the
screen side (m1 frames 494/554, x~150, terrain ~(100,70,58) against sky ~(195,143,108)), see docs/owner_sheet_s7007_melt_219.png row pair 3.
Hypotheses:
- H-window: the FWDWIN box (tools/apply_s6901_fwdwin.py: per axis width min(bounds,64), centre eye + K*forward, K=30) does not cover the 21:9 frustum
  sides; its side/corner is what shows. Fix: widen the lateral extent with the aspect (or shift K less at wide aspects), watch the pool/heap caps.
- H-bounds: the level's own terrain bounds end there (real map edge). Then nothing to fix but fog/melt by lateral distance.
- H-cutoff: the radial far cutoff (s6418 x s6904 clipmul 0.25 at dd4) clips side cells. Then the edge would be curved, not a box corner.
Discriminator (one run, no build): `env CULL=1 ASP=21:9 CW=1260 CH=540 zsh scratch/s7007/arm.zsh 4 4 w1 "ROGUESQ_DD_FWDWIN=tog ROGUESQ_DD_MELT=1" 120 60`
(FWDWIN toggles on odd mach seconds). Score with tools/g5e_edge_score.py raw 4 2600 50 24e6 per third (side thirds are the test). Outcomes: side-third hard80
changes with FWDWIN parity and the corner moves -> H-window; the edge sits still in world space across both parities -> H-bounds; curved edge -> H-cutoff.
Also log the window: if apply_s6901 has no log, add one (eye cell, box x0..x1/z0..z1, heading) under an env flag in the fixup and rebuild once.
Then fix and give the owner a before/after sheet at 21:9 and 16:9. Delete raws (disk ~22 GB free; each raw ~8 GB, keep only one at a time).
