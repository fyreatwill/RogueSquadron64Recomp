# NEXT: FPS60 frame-locked tick-count timers in NPC AI (20-tick cadence) - idiom audit + fix
HYPOTHESIS-ID: g3-fps60-tick-timers

State (s6819): lvl14 scrape thread closed (step quantum s6817 + damage quantum s6819; scrape hp 40 = 30 Hz).
First: fold SOAK-RESULTS s6819_scrapedmg_b60fix_s2/s3 (expect scrape hp 40 via tools/g3_scrape_damage.py 60
scratch/s6819/b60fix_s{2,3}.rand.txt; deaths via tools/g3_death_time.py). If either != 40, reopen.
Side datum s6815: npcWingmanBehaviorByMode 0x800D860C and initActorMotionParams 0x800F28F4 fire every 20 TICKS
(0.667 s at 30 Hz, 0.333 s at FPS60, seed-independent) - AI decision cadence doubles at FPS60.
Hypotheses:
  H-counter: a per-NPC (or global) integer tick counter (addiu +-1, compare 20/0x14) gates the re-plan -> frame-locked.
  H-global-frame: gate is (global frame counter % 20) on e.g. 0x8013889C (the tick%3 counter used by bolt hit tests).
  H-dt-timer: a float timer decremented by dt (then the 20-tick observation is wrong) -> close.
Step 1 (offline): read the callers of 0x800D860C / 0x800F28F4 in ../N64Recomp/RecompiledFuncs for the gate; then
  grep-enumerate the idiom class (lbu/lh counter, addiu -1/+1, slti/beq vs constant, store back, in per-tick NPC
  update functions) - classify each site frame-locked vs dt-based, like tools/g3_dt_quantum_audit.py.
Step 2: fix the class under ROGUESQ_FPS60 only (count at 30 Hz: advance the counter every other 60 Hz tick or
  scale the threshold), env off-switch, one build, arms a30 / b60fix / b60off on lvl14 seed 1 (scratch/s6819/arms.sh
  pattern), discriminator: cadence of 0x800D860C calls per game s equal to 30 Hz in the fix arm.
