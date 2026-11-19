# NEXT (s7630)
HYPOTHESIS-ID: g6-upstream-features

G6c step 4 continued: L0-L5 STANDINS=1 dd4 300 s holds are clean (s7629). 13 remain queued: scratch/agent/soak_queue/s7628_standins_hold_L{6..18}.sh.
1. Fold any new SOAK-RESULTS verdict lines (alive, fatal, stall_arms, tag= level_ok). If the host is idle (HIDIdleTime > 300 s, nothing running),
   run up to 4 in-session sequentially like scratch/s7629/run4.zsh (move each recipe to soak_queue/done/ first).
2. Any crash/stall with STANDINS=1: rerun that level with STANDINS unset (same recipe) as control. Stand-in-only -> root-cause in
   src/main/rs64_standins.cpp / tools/apply_s7625_standins_far.py (name the writer). Both -> not ours (G4 rule).
3. When >=17/19 pass with no stand-in-only failure: owner note in docs/OWNER-OPT-INS.md (ROGUESQ_STANDINS=1, dd>1 only), point at
   docs/owner_sheet_s7628_standins_on_off.jpg (optionally regenerate with the s7629 --cluster scorer, whose crops land on the object),
   ask the owner to judge look/default. Default stays off.
Outcomes: all clean -> G6c closes on the owner's look; stand-in-only crash -> fix first.
Hygiene: one game at a time; never touch build/saves or clear ROGUESQ_NO_SAVE_WRITE.
