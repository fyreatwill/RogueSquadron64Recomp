# NEXT: fold the s6832 FPS60 bundle holds, then the next ladder rung
HYPOTHESIS-ID: g1e-fps60-bundle-regression

Context: G1e FPS60 rate classes closed (s6817-s6831), fixes tabulated in docs/FPS60-FIXES.md, owner asked to judge
feel. Queued: scratch/agent/soak_queue/s6832_fps60bundle_lvl1_dd4.sh and _lvl10_dd4.sh (300 s FPS60+dd4, all fixes).
Step 1: read SOAK-RESULTS tail + scratch/agent/m6/g1_lvl{1,10}s6832_fps60bundle/summary.
Hypotheses: H-clean (alive_at_end=1, crashlines=0, vi_stalls30s=0 both levels -> bundle qualified, note in
FPS60-FIXES.md) vs H-regress (a crash/stall -> backtrace it, then bisect by the six =0 switches in ONE run set:
each switch off alone on the failing level, same recipe) vs H-harness (rc=3: switches missing -> rebuild with the
regen order make_elf -> N64Recomp -> fixup_game_funcs (runs the fps60 fixups) -> cmake).
Step 2 if H-clean: no owner reports pending -> take the ladder: G5 renaming sweep is the last rung, but iron rule 14
says renames read as churn; prefer an engineering item if one appears in CURRENT-TRUTH Next steps (owner reports first).
