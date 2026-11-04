# NEXT: fold the true lvl10 hold, then re-earn 300 s of flight where the audit found less
HYPOTHESIS-ID: g1-true-flight-hold

Why: s6865 showed 65 of 117 retained G1 logs reporting hold>=280 s flew <280 s. Those runs were clean but short. lvl5 dd4 now has 306 s (s6865 arm A); the rest of the owner path (FPS60+dd4) does not.
First: fold s6865_truehold_lvl10_dd4 from SOAK-RESULTS.md (124 s was the most lvl10 dd4 had flown).
Then: from scratch/s6865/hold_audit_all.txt list each level whose best FPS60+dd>1 flight is <280 s, and queue one soak per level, copying soak_queue/done/s6865_truehold_lvl10_dd4.sh (HOLD_S=300, MISSION_INIT default, SOAK_TIMEOUT=900). Read them as they land; update G1-FRAMEBUFFER-COVERAGE or CURRENT-TRUTH with true flight seconds.
Hypotheses: H-holds (each level flies >=280 s clean: the old claim stands, with real numbers) / H-late (a crash, stall or death appears only after the old 124-230 s window: new datum, capture a backtrace and name the writer) / H-end (mission ends or player dies before 300 s: record the true ceiling, not a failure).
Runs: foreground up to 600 s or queue a soak. Do not end the turn to wait.
Ask owner when a human is next on: add tools/regen_replay.sh + regen_verify.sh to the CLAUDE.md regen order (owner file, not edited).
Owner judges: docs/owner_sheet_s6860_lvl10_hud_ab.png, docs/owner_sheet_s6861_pause_hud_ab.png.
