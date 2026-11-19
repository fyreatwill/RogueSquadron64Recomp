# NEXT (s7624)
HYPOTHESIS-ID: g6-upstream-features

G6c step 3 per docs/G6C-STANDINS-PLAN.md: show the stand-ins make objects visible earlier, same run.
Hypotheses: H-visible (stand-in pixels appear at distance in on seconds, absent in off seconds, before the real spawn);
H-culled (submitted but the bucket/view test drops them: no pixel difference on vs off); H-double (an object drawn twice at the
spawn moment); H-budget (bucket fills, real objects vanish in on seconds).
1. Add to rs64_standins.cpp (one build): per tog window, count of submits whose item is within the camera far range, and a
   bucket-fill read if addNpcToVisibilityBucket's bucket count can be located (read its code once: funcs_12.c); log spawn events
   (item+6 leaves 0xFFFF) with the frame number so a frame dump can be matched to it.
2. One run per level (L1 and L4 = ROGUESQ_FORCE_SAVE_MISSION=4), dd4, ROGUESQ_STANDINS=tog +_LOG=1, SHOTS each second for 20 s in
   flight (windows are now whole-second aligned: shot parity = arm). Scratch dir scratch/s7624.
3. Score: pixel diff of consecutive on/off shots restricted to far terrain (top third of the ground area); look for object
   silhouettes present only in on shots. Owner sheet of matched pairs.
Outcomes: H-visible -> step 4 (19-level 300 s soak queue + owner sheet); H-culled -> read the view test radius (state +0x38 scale);
H-double -> tighten the spawn test; H-budget -> cap stand-in submits per frame.
Hygiene: one game at a time; never touch build/saves or clear ROGUESQ_NO_SAVE_WRITE; on battery use ALLOW_SLOW=1 (functional only).
