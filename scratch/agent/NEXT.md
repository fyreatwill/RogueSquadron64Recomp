# NEXT: L12 dd6 bundle cut edge — eye-to-edge K gate (keep 60 fps, lose the hard horizon)
HYPOTHESIS-ID: dd6-bundle-l12-horizon
Context (s7045): on L12 at 16:9 the bundle's K=0.6 off-map cull leaves a hard jagged horizon where dd6off draws a soft fogged band;
retail dd1 draws only fog there (band = extension ground). K=0.8 is invisible (0.07 / 0% px) but only 54.1 fps on L12 (K=0.6 59.7,
K=1.0 43.9; same-run hold, rsp -1.11 vs -3.95 ms). Eye sits near the z map edge (win z=-47..-65, dims 88x88) looking outward.
Unit (one build, all arms in one run): add ROGUESQ_DD_OFFMAPCULL_KEDGE=<k2>[,N] in src/main/upstream_compat.cpp (s7034 K path): an
off-map cell whose clamped edge lies on the map side the eye is within N cells of (default N=8) AND in the forward half-plane uses
K=k2 (0.8); all other off-map cells keep K. Log per phase how many cells took k2 ([s7046] counter, positive control: >0 on L12).
Then: (1) frozen poses L12 (scratch/s7045/run.zsh, arms dd6off / dd6b / kedge) score vs dd6off; (2) tog3 hold L12 R=-1,2,2 with
KEDGE off/on in phases 1/2 (cost); (3) one tog3 hold on L1 (cost must stay within 0.3 ms of K=0.6).
Outcomes:
- H-gate: kedge <=0.1 on L12 poses AND L12 >=58.5 fps -> fold KEDGE=0.8 into the s7037 bundle (main.cpp:12049), update OWNER-OPT-INS.
- H-whole: kedge costs ~ the same as K=0.8 (eye near the edge most of the flight, culled cells ARE the outward band) -> the cost and the
  band are the same cells; report the 60-hard / 54-soft choice to the owner (already in OWNER-OPT-INS) and close the thread.
- H-partial: invisible but 55-58 fps -> try N=4 / k2=0.7 in the same build via tog3, pick the best, owner chooses.
