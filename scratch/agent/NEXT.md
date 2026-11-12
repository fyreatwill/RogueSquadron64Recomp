# NEXT: Retina owner sheet (flight crops RETINA 0 vs 1), then owner picks the default
HYPOTHESIS-ID: retina-render-scale
Context: s7203 added opt-in ROGUESQ_RETINA=1 (swap chain at backing pixels). s7204 measured flight cost at the owner recipe:
free (fl_shown 59.9-60.0, GPU median +0.1 ms, 0 gaps > 250 ms, 0 crashes; scratch/s7204, tools/s7204_ring_cost.py).
Unit: one owner sheet so the owner can judge sharpness in flight. Same scene both arms, phase-gated by the autopilot timeline
(tools/g1e_owner_quiet_arms.zsh route, LEVEL=4, t ~ 150 s in flight): screencapture -x at fixed offsets after launch in each arm,
crop the same 1:1 region (scratch/s7203/crop_c3.png style), score with scratch/s7203/hf.py (expect R1 > R0, ~0.58 -> ~0.8).
Hypotheses: H-sharp (R1 visibly sharper in flight like attract) vs H-same (flight content is low-frequency, no visible gain:
then RETINA stays an opt-in with the cost note). Positive control: R1 frame downsampled 2x and back up must score at the R0 level.
Deliver docs/owner_sheet_s7205_retina.png, add a line to docs/OWNER-OPT-INS.md. Default stays off until the owner says.
