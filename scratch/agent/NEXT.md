# NEXT: G3c(a) make the height-fade factor f live, rerun y vs nofade
HYPOTHESIS-ID: g3c-owner-visual

s6364 result: hook at 0x80011788 is on drawn cells (ycontrol +50 visibly spikes terrain), but every logged f was 0 (rs64_s6363_f is written in funcs_10.c radfade2 block after L_8004AA74, per cell colour callee).
Hypotheses: H-stale (colour callee runs after the height hook or for a different cell, so f is stale/0), H-near (nearly all cells are within r0=26 so f=0 is real and only far cells matter; log was sampled 41 times, mostly early), H-ok (f works, fade genuinely no effect on jump).
Work unit (one build, one run): in tools/apply_s6363_heightfade.py hook, count f>0 and f>0.99 over the run and print every 2000 calls; also compute d in-hook from cell position (same xo/zo/cxf/czf formula as radfade2) as f2 and log f vs f2 agreement. Regen via fixup (not hand edit), cmake, rerun soak recipe (copy running_manual/s6363_g3c_heightfade.sh, y + ylow + nofade) and score with `python3 tools/g3c_horizon_score.py <fbd> 3600` (flight frames only).
Outcomes: f>0 never but f2>0 -> H-stale, use f2. f>0 often and jump_med unchanged -> H-ok, y-fade not the edge cause; take next lead (fade outermost ring / haze scaling). jump_med drops >0.03 -> adopt into DRAW_DISTANCE bundle, ask owner.
