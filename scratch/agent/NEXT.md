# NEXT: G1e FPS60 close-out - fold the s6831 ramp soak, then an owner-facing FPS60 summary
HYPOTHESIS-ID: g1e-fps60-closeout

Context: s6831 closed the last G1e FPS60 rate class (|K|>1 int steps; advanceNpcOnCurvedPath +0x1E ramp fixed,
lvl14 a30 0.267 s / off 0.133 / fix 0.233-0.258, fix n=2). All of CURRENT-TRUTH's ladder rungs are closed or wait on
owner judgement (G1d sheet, G3c). Queued soak: scratch/agent/soak_queue/s6831_intstep_fix_lvl14.sh (400 s FPS60 fix arm,
prints the ramp table).
Step 1: read SOAK-RESULTS + scratch/agent/soak_results/s6831_intstep_fix_lvl14_*.log. Hypotheses: H-fixed (ramp-up and
wind-down medians within one 30 Hz tick of 0.267 s, n>=5) vs H-phase-bias (fix median consistently ~0.233, i.e. the
+1 seed tick plus the 0/1 step phase loses one 30 Hz step -> seed the accumulator, or step on the first tick after a
seed) vs H-path (too few ramps again: lvl14 NPC path churn; pick another level from the s6822 census).
Step 2 (engineering, not doc-only): write docs/FPS60-FIXES.md - one table of every FPS60 fix switch
(FPS60_TICKS, FPS60_DESPAWN, FPS60_SCRAPE_DMG, FPS60_FQUANTA, FPS60_INTSTEP, ...: grep tools/fixup_fps60_*.py and
src/ for getenv("ROGUESQ_FPS60), what each restores, the verifying session and numbers), and link it from
docs/OWNER-OPT-INS.md, so the owner can judge FPS60 feel with every fix named. Then ask the owner for the FPS60 feel
verdict in CURRENT-TRUTH Next steps.
If H-phase-bias: fix it in tools/fixup_fps60_int_step.py and re-run scratch/s6831/lvl14.sh (fix arm only + a30 control).
