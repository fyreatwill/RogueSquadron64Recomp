# NEXT: why NPC formation spawns run ~0.7x per game second at ROGUESQ_FPS60=1 (lvl14, dt 1/60)
HYPOTHESIS-ID: g3-fps60-spawn-rate

State (s6814): the lvl14 "late cutscene" at FPS60 is the passive player's death (flag 0x100 in 0x8010CA1C on the hp-0
tick, 7/7 runs). FPS60 takes ~half the 50-hp hits per game second (0.029-0.069 vs 0.107-0.140/s). Per-hit damage, hp
regen (1.945/s) and mission timers are dt-exact. Rand-caller rates on one same-seed pair: spawnNpcFormationWithRandomOrientation
(0x80040AE0/B5C/C28/CBC 5.00 -> 3.74/s; 0x80040E6C/F50 15.0 -> 10.5/s), composeRandomRotationMatrix/scaleVec3ByRandomRange,
npcPowerGeneratorHandleDestruction: 0.70-0.75x per game s at FPS60.
Data on disk (offline first, no build): scratch/s6814/{a30,a30_s1,a30_s3}.rand.txt (30 Hz) and {b60,b60_s1,b60_s2,b60_s3}.rand.txt
(FPS60); game time = 800fa730 row ordinal / 30 or / 60; each row "idx VI callerPC seed".
Also fold the queued soak s6814_bootfreeze_ab first (boot freeze at fs=39 / VI 128 in a30_s2; preempt point on vs off).
If any boot froze, that is a side-effect stall to root-cause (G4 rule: fix the one a soak hits) - lldb attach to a frozen
boot, read every guest thread's state/PC.
Hypotheses:
  H-spawn-timer: formations spawn on a timer/countdown that runs slow at dt 1/60 (e.g. a countdown decremented by a
    constant per tick but compared against a dt-scaled threshold, or a wave timer clamped per tick).
  H-kill-chain: formations respawn after the previous ones die; wingmen/AI kill slower per game second at dt 1/60
    (AI aim/turn per tick, bolt collision), so fewer respawns -> fewer shooters -> fewer player hits.
  H-proximity: spawns trigger on player position/distance; the FPS60 path differs after 10 s (diverged sim).
Discriminator (offline): group rand calls from 0x80040AE0..0x80040F50 into spawn events (same VI cluster), print game
  time per spawn event for all 7 runs, plus NPC destruction events (0x8007668C cluster, 0x800B08D8 and other debris callers)
  per run. Fixed spawn game times across seeds/arms with longer gaps at FPS60 -> H-spawn-timer; each spawn shortly after a
  destruction, destruction rate lower at FPS60 -> H-kill-chain; spawn times following player position -> H-proximity.
  Control: the 0-10 s identical-sim window must give identical spawn times in both arms.
Then: for the selected term, find the writer/counter in generated code and qualify an FPS60-only fix (scale by dt) with
a seeded 3+3 rerun of scratch/s6814/seeds.sh (50-hp hit rate per game second must match the 30 Hz arm).
