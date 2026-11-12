# NEXT: G3 in-flight fidelity at RETAIL settings (4:3, dd1, no FPS60): L17 (RESUME, capture on disk), then L18 (CURRENT-TRUTH item 36)
HYPOTHESIS-ID: g3-retail-43-sweep
State (s7179): retail 4:3 H-equal on L0-L16. The L17 capture already exists: scratch/s7141/L17r.cap + L17r.raw, cap_L17r.txt says
window (225.0, 46.0, 1062.0, 828.0), frames 10970, fails 0. DO NOT re-run L17. Post it first, then run L18. Item 36 closes after that.
STATUS RULE (s7179): never write WORKING to scratch/agent/STATUS yourself. Write STATUS only at the end (DONE/BLOCKED).
WAIT RULE (s7179): sum_L*r.txt is ALWAYS 0 bytes. Wait for a run with `while pgrep -f s7141_arm.zsh >/dev/null; do sleep 5; done`
  (or a Monitor on that), never on `[ -s sum_*.txt ]`.
FIRST: CURRENT-TRUTH is ~59973 bytes. Keep any edit byte-neutral (replace text, don't add), or the >60000 maintenance check trips.
Post L17 (FID_MAINRUN=1 always):
  env FID_MAINRUN=1 zsh tools/s7177_post_lvl.zsh 17        (CONTROL, fsum main + shift-2, rectfit; CTRL must PASS)
  env FID_MAINRUN=1 SPLIT=103,205 SHEET_LABEL=4:3 zsh tools/s7160_fit_post.zsh scratch/s7141 L17r <best rect> docs/owner_sheet_s717x_L17_43_fidelity.png
  L17 is dark/smooth (trench): the shift-2 control was weak at 21:9 too. Judge it by meand ratio + sheet, and by flight swaps only if a
  results/level-select screen is inside the window (L16 lesson). Then rm L17r.cap L17r.raw.
Run L18:
  env CW=320 CH=240 zsh tools/s7141_arm.zsh 18 L18r "ROGUESQ_FPS60=0 ROGUESQ_DRAW_DISTANCE=1 ROGUESQ_ASPECT=4:3 ROGUESQ_G5B_FRAME_EVERY=1 ROGUESQ_G5B_FRAME_FROM=7500 ROGUESQ_G5B_FRAME_MAX_MB=12000"
  Check cap_L18r.txt window (..., 1062.0, 828.0), then post it the same way.
Hypotheses per level: H-equal (centre <= ~0.015, 0 flight >0.05 beyond lag/HUD), H-hole (tools/s7166_holetris.py), H-lag (dup pframe,
or the swap's image appears only in a later pframe), H-tool (CTRL fails / shift-2 no worse / row-gap crop).
Disk: df >= 20 GB before each run. Owner save rule: NO_SAVE_WRITE stays, no SAVE_FROM.
