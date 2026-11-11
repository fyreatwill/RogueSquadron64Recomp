# NEXT: G3 owner-recipe fidelity at 21:9 (CURRENT-TRUTH item 30; s7131 did 16:9 only on L1/L4)
HYPOTHESIS-ID: g3-fidelity-219
State (s7140): 21:9 hole fixes clean on L1/L4/L6/L15 (0 flight holes each vs controls 77-95%). Item 29 closes on the owner's look.
Question: at the owner recipe with ROGUESQ_ASPECT=21:9, does RT64's presented window match angrylion replays of the same RDP stream?
Hypotheses:
- H-equal: mean|d| and frac>40 within the s7122/s7131 floors (L1 ~7.8-8.4 / 0.024-0.028; L4 6.8 / 0.017) on every scored swap.
- H-wide-rt64: RT64 differs only in the extended side columns (x outside the central 4:3 band): a renderer path (scissor, guard band,
  texrect at wide x) that the 16:9 run never exercised.
- H-align: diffs are frame misalignment in fast rolls only (check best-of +-2 lag; single outlier frames).
Run (one game at a time, ~5.5 min each, delete .cap/.raw after scoring; disk ~61 GB free):
  copy tools/s7138_arm.zsh -> it already records stream + window at CW x CH; use CW=504 CH=216 (21:9 content)
  env CW=504 CH=216 zsh tools/s7138_arm.zsh 15 F1L15 "ROGUESQ_ASPECT=21:9 ROGUESQ_G5B_FRAME_MAX_MB=9000" 120 180
  env CW=504 CH=216 zsh tools/s7138_arm.zsh 6 F1L6 "ROGUESQ_ASPECT=21:9 ROGUESQ_G5B_FRAME_MAX_MB=9000" 120 180
  replay with tools/s7139_post.zsh (flight start from s7138_bindegen), then score with tools/s7122_fidelity.py
  (read its usage + the s7131 PORTING-STATE entry for the rect/lag flags; the content rect at 21:9 differs from 0,9,369,216 —
  measure it from the raw first). Add a column split (central 4:3 vs side bands) to the score: that is the H-wide-rt64 discriminator.
Positive control: a deliberately shifted (1 frame lag off) pairing must score well above the floor, or a pass is not a result.
Owner save rule applies. CURRENT-TRUTH ~59.8 KB: keep edits net-zero (Step 0 triggers at 60000).
