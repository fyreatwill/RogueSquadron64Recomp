# NEXT (s7625)
HYPOTHESIS-ID: g6-upstream-features

G6c step 3b (docs/G6C-STANDINS-PLAN.md "Step 3 result"): stand-ins are culled by the game's view test transformVec3ToNpcLocalWithScale
(0x8001DC34): 0.2% accepted (s7624). Find WHICH bound rejects them, then widen it for stand-in calls only.
Hypotheses: H-far (the far test at 0x8001E078, $f2 vs $f0, rejects: upstream multiplies $f0 by dd there); H-box (the +-125
camera-space box at 0x8001DCEC low / 0x8001DD38 high, constants *0x8000093C / *0x80000940, rejects: upstream widens it by dd and
relies on RT64 HLE far matrices, which our LLE path lacks); H-side (frustum x/y half-extent test ~0x8001DEAC rejects: objects simply
off screen, correct cull).
1. Read transformVec3ToNpcLocalWithScale in /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs (grep the RECOMP_FUNC) and
   list each reject exit. New tools/apply_s7625_viewtest_reason.py (RS64_REPLAY): when a host flag rs64_standins_in_call is set,
   record the exit taken (box-low, box-high, far, side-x, side-y, pass) and the camera-space xyz; rs64_standins.cpp sets the flag
   around its addNpcToVisibilityBucket mips_call and tallies per second: `[standins-why] box=.. far=.. side=.. pass=.. zmed=..`.
   Positive control: pass count == added count from s7624's counter in the same run.
2. Same arms as s7624 (scratch/s7625, L1 + L4 dd4, ROGUESQ_STANDINS=1 +_LOG=1, HOLD 130, ALLOW_SLOW=1 on battery).
Outcomes: H-far dominant -> widen $f0 by dd for stand-in calls only (no matrix risk), rerun the s7624 flicker test (ROGUESQ_STANDINS=frame
+ STANDINS_DUMP=40:46:90 + tools/s7624_flicker_score.py --control); H-box dominant -> the fixed-point reach is the real limit: design
the LLE answer (place at cam + (p-cam)/k with scale 1/k so the matrix stays in reach; check terrain occlusion) before widening;
H-side dominant -> stand-ins are correctly culled, the pop-in is elsewhere (spawn radius vs our dd far): reread upstream.
Hygiene: one game at a time; never touch build/saves or clear ROGUESQ_NO_SAVE_WRITE; fb dumps are ~180 MB per arm (gitignored).
