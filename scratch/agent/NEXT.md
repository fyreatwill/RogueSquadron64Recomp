# NEXT: FPS60 terrain-scrape response (lvl14 15.4 s contact: 2 contacts at 30 Hz vs 7 at FPS60)
HYPOTHESIS-ID: g3-fps60-scrape

State (s6816): the whole lvl14 "FPS60 dies later" chain starts at one passive-player terrain/object scrape at 15.4 s.
updatePlayerCraftPhysics (0x800B1BE8) calls 0x800FEF10 (mis-named stepObjectOrientationTowardTarget; returns 1 = contact,
2 = other) after integrateCraftVelocityAndCollide 0x800AECF8; on 1 it takes 20 hp (0x800A5734) per tick (shield +0xC8 first),
no cooldown. 30 Hz: contacts at 15.40, 15.63 s, exit vel (1.61,-1.57,-0.10). FPS60: 7 contacts 15.40..15.88 s, exit vel
(1.33,-1.80,+0.20). Same in seeds 1-3. Data: scratch/s6816/batch1/*.rand.txt (hp rows b017dd00 + tick rows with the
player record 0x80137DB0: pos words 4..6, hp word 51).
Hypotheses:
  H-push: the contact response pushes the craft out by a fixed distance (or a fixed fraction of penetration) per TICK ->
    half the separation per game s at FPS60 -> stays in contact longer, more contact ticks.
  H-damp: velocity reflection/damping uses a per-tick factor (v *= k each contact tick) -> twice the damping per game s ->
    different exit velocity.
  H-dmg-only: response is dt-exact and only the per-contact-tick damage doubles (then exit velocity would match - it does
    NOT, so H-dmg-only alone is already unlikely).
Step 1 (static): disassemble 0x800FEF10 and 0x800AECF8 (generated C comments in ../N64Recomp/RecompiledFuncs; mind overlay
  duplicates - dedupe by address) and list every constant that touches position/velocity without a dt multiply.
Step 2 (one build, both arms): FPS60-only fix (scale the per-tick term by dt*30, or by (1-(1-k)^(dt*30)) for a damping
  factor) behind the FPS60 path, env ROGUESQ_FPS60_SCRAPE=0 restores. Rerun scratch/s6816/seeds.sh with s1 only per arm
  (deterministic) plus a b60 arm with the fix; also add per-tick player vel rows across 15.3-16.0 s (tick rows already have pos).
Discriminator: fixed FPS60 arm reproduces 2 contacts (or the same contact game-time span) and the 30 Hz exit velocity
  within ~5% -> fixed; then the 50-hp hit rate per game s and death time should move toward 30 Hz (81 s for seed 1).
Damage per contact tick: if contacts match after the fix, leave damage per contact as retail; if contacts are inherently
  per tick, scale damage by dt*30 at FPS60.
Side datum (s6815): npcWingmanBehaviorByMode 0x800D860C / initActorMotionParams 0x800F28F4 fire every 20 ticks (2x per game
  s at FPS60) - check wingman radio chatter rate at FPS60 later.
