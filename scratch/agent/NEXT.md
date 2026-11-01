# NEXT: G1c phase 2 closure after the s6701 perspNorm far cap
HYPOTHESIS-ID: g1c-phase2-closure

s6701: frame cost no longer binds (lvl5 dd4/dd6 ~30-32 tasks/s on -O2). dd8's centre-box render was perspNorm 1 from our
s6031 far scaling, now capped (tools/apply_s6031_far.py s6701, ROGUESQ_DD_PNORM_CAP=0 = old). lvl5 terrain table (64x64) is
fully covered at dd4.
1. Fold SOAK-RESULTS lines for s6701_pnormcap_dd8_lvl1 / lvl10 (python3 tools/g1c_phase2_fold.py scratch/agent/m6/<tag>), and
   view late fbd frames: full-screen flight, no centre box. A box or crash there -> backtrace/threshold that camera.
2. FPS60 dd4 cost without the pause: the recipe START at t=74 s pauses the mission until a later `a`. Run lvl5 dd4 FPS60 and
   dd4 with --tmin 140 in the fold (or FL_START tweak), same batch. Hypotheses: H-fps60-affordable (>=55 tasks/s, gfx <16 ms)
   vs H-fps60-cost (game thread binds below 50).
3. Owner sheet: lvl1 + lvl5 dd1 / dd4 / dd8 (capped) late flight frames, tools/contact_sheet.py; update docs/DRAW-DISTANCE.md
   (dd>4 adds no terrain on lvl1/lvl5; dd8 renders correctly only with the s6701 cap). Then close G1c phase 2 and move to the
   next ladder rung (G3 render fidelity), defaults unchanged.
