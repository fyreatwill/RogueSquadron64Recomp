# NEXT (s7629)
HYPOTHESIS-ID: g6-upstream-features

G6c step 4: crash-free 300 s holds with ROGUESQ_STANDINS=1 at dd4 on all 19 levels, then the owner sheet.
s7628 proved by eye that stand-ins draw early (docs/owner_sheet_s7628_standins_on_off.jpg; docs/G6C-STANDINS-PLAN.md "Step 3 proof").
1. 19 recipes are queued: scratch/agent/soak_queue/s7628_standins_hold_L{0..18}.sh (SOAK_NEEDS_IDLE=300). Fold the verdict lines in
   SOAK-RESULTS.md (alive, fatal, stall_arms, level_ok via tag= line). If the host is idle now and they have not run, run 1-2 in-session
   (`zsh scratch/agent/soak_queue/s7628_standins_hold_L5.sh`), moving each to done/ first so the loop does not repeat it.
2. Any crash/stall with STANDINS=1: rerun that level with STANDINS unset (same recipe, same dd4) as the control. Crash only with
   stand-ins -> root-cause in src/main/rs64_standins.cpp / apply_s7625_standins_far.py (name the writer). Crash in both -> not ours, G4 rule.
3. When >=17/19 pass with no stand-in-only failure: owner note in docs/OWNER-OPT-INS.md (ROGUESQ_STANDINS=1, dd>1 only), point at the
   s7628 sheet, and ask the owner to judge the look / default. Keep the default off.
Outcomes: all clean -> G6c closes on the owner's look; stand-in-only crash -> fix that first.
If nothing ran and the host is busy: offline, extend tools/s7628_standins_sheet.py with a shimmer filter (reject diff cells whose
off-neighbour pair also flickers in window 2 at the same screen region) so the scorer stops counting texture shimmer.
Hygiene: one game at a time; never touch build/saves or clear ROGUESQ_NO_SAVE_WRITE; check idle first.
