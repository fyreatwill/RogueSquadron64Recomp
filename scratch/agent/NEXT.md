# NEXT: why FPS60 (dt 1/60) halves the share of enemy impacts that damage the player (lvl14)
HYPOTHESIS-ID: g3-fps60-hit-prob

State (s6815): impact effects near the player (randomlyScaledEffectNpcHandler 0x800606F4 onsets) per game s are the
same in both arms, but impacts->hp hit is 10.7% (30 Hz) vs 5.3% (FPS60), 7 seeded runs (tools/g3_fps60_hit_attrib.py
scratch/s6814 a30 a30_s1 a30_s3 b60 b60_s1 b60_s2 b60_s3). Every hit is preceded by an impact (33/33).
Hypotheses:
  H-lead: enemy aim leads the player using a per-tick displacement (velocity in units/tick) -> at dt 1/60 the lead is
    half -> shots trail the craft. Predicts: miss vector parallel to player velocity, FPS60 miss distance ~ v*t_flight/2.
  H-collision: projectile-vs-player test (radius, swept segment or tick-count lifetime) misses more at shorter steps.
    Predicts: FPS60 closest approach within the hit radius without registering, or projectiles expire earlier in game s.
  H-splash: damage from an explosion is applied on a per-tick window -> half the exposure. Predicts: hits from splash
    only, and the damage path keyed to effect age in ticks.
Step 1 (static, no build): find who spawns the 0x800606F4 effect (caller of randomlyScaledEffectNpcHandler's object
  type), the enemy projectile pool and the aim routine (look for atan2/lead math using the player object 0x80137DB0
  position +0x10..0x18 and velocity), and the damage application to player hp (object +0xCC word 51).
Step 2 (one build, both arms): add xtrace marker rows (tools/fixup_rand_trace.py pattern, s6752) at the projectile
  spawn (aim point, player pos+vel) and at the impact/damage site; rerun scratch/s6814/seeds.sh 3+3 with the same seeds.
  Control: in the identical-sim window 0-10 s the per-shot rows must match bit-for-bit between arms.
Discriminator: per-shot lead error along player velocity (H-lead) vs closest approach inside radius without a hit
  (H-collision) vs damage keyed to effect age (H-splash). Then fix the selected term FPS60-only (scale by dt) and
  requalify: 50-hp hit rate per game s must match the 30 Hz arm.
Side datum to fold later: npcWingmanBehaviorByMode 0x800D860C / initActorMotionParams 0x800F28F4 run every 20 ticks
(2x per game s at FPS60) - check whether wingman radio chatter doubles at FPS60 (0x80066EE4 calls).
