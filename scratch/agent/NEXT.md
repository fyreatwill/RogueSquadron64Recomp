# NEXT: why the lvl14 in-mission cutscene starts ~20 game-s later at ROGUESQ_FPS60=1 (dt 1/60) than at 30 Hz
HYPOTHESIS-ID: g3-fps60-timeline

State (s6813): the destruction effect itself is dt-scaled (H-match). But with dt pinned 1/60 and 1 VI/tick, the cutscene
flash lands at port tick ~6705 = 111.7 game-s vs retail/30 Hz-port t2737 = 91.2 game-s (s6812 launch t0 -5.157 assumed for
FPS60 too; only 18 dropped VIs). Owner plays at FPS60, so mission scripting that runs slower per game second is a fidelity defect.
Data already captured (offline, no build first):
  30 Hz port: scratch/s6812/pair/port.rand.txt (dt 1/30 pin)   FPS60: scratch/s6813/port.rand.txt (dt 1/60 pin)
  retail: scratch/s6812/pair/retail/oracle.log (xtrace rows). Rows 800fa730 carry m=80165ed0 (snapshot) and m=8011a880 (globals,
  words 28-31 look like floats: player pos?), m=8010c9e0 (18 words), m=8010ff30.
Hypotheses:
  H-trigger-pos: the cutscene fires on player position/progress; the player's path per game second differs at dt 1/60
    (integration, or a speed term applied per tick without dt) -> player position vs game time diverges early.
  H-framecount-slow: a script timer counts 30 Hz units via a fixed per-tick step that FPS60 halves (e.g. a 0x8011A8F4-style
    counter consumed as "frames at 30 fps"), so in game seconds it runs 2x slow -> some script word advances half as fast per s.
  H-t0: the FPS60 launch t0 differs (VI count vs wall) and there is no delay -> HUD-off at the same port TICK/2 as 30 Hz.
Discriminator (offline): (1) map each arm's tick -> game time (30 Hz: tick/30, FPS60: tick/60) and find the HUD-off/cutscene
  start tick in each from the rand trace (caller-set change, as g3_song_windows/g3_rand_ticks did) - settles H-t0 without wall
  time; (2) diff the m=8011a880/8010c9e0 words per game second between arms: a word advancing 0.5x per s at FPS60 names the
  slow timer (H-framecount-slow); player position words diverging early select H-trigger-pos.
  Control: words known dt-scaled (e.g. dt 3c888889 vs 3d088889 itself; frame counter 0x8011A8F4 must be 2x per s at FPS60).
If a slow script timer is named: find its writer (static read / xtrace), fix as an FPS60-only patch (scale by dt), qualify
with a same-recipe FPS60 run where the cutscene lands at ~91 game-s.
