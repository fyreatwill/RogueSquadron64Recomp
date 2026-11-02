# NEXT: G3 bonus missions 18 and 19 — sim/frame match with the s6771 bonus-mission recipe
HYPOTHESIS-ID: g3-mission18-pinned

s6771 closed mission 17 (race, 458 ticks identical). Missions 18/19 = save +0x31=17/18 (run.sh adds +0x39=0x60).
Unknowns: when each arm reaches the level select and picks (port ~24 s / ~32 s, retail ~38 s / ~51 s for m17), whether the
mission needs a press after the pick (m17 did not; normal missions show a briefing), and how long it lasts unsteered.
Work unit:
1. Port probe (75-90 s, no retail): env SAVE_FROM=<lvl18.eep from run.sh or tools/g3_eep_patch.py> SECS=90 CAP0=30
   AP=6:start,...,31:start zsh tools/g3_port_capture.sh scratch/s6772/probe18 ; contact sheet of captures; grep
   '[lvsel] tick#.*ret=' and load_level_hmp in run.log. Add presses only if the mission waits on a screen.
2. Paired run: env G3_MIN_TICK=0 PRESS=6:start,...,51:start[,+N if a briefing] AP=6:start,...,31:start[,...] DWARM=30 ARM=20 \
     POKE=800FA730:29:30:3d088889,800FA730:0:80003470:1:1 RSECS=<race/mission end+> PSECS=.. CAP0=33 NDUMP=40 DSTEP=1 FARM=54 \
     zsh tools/g3_mission/run.sh scratch/s6772/r18 17 ; then rerun offline with G3_SNAP_TICKS=800FA730.
   Retail press timing: the level select accepts the pick only after its intro animation (retail pick at 51 s for m17).
   Never leave a Start press inside the mission (it pauses; s6770 run 2).
Discriminating outcomes: rand/NPC identical over the whole trace (or until a song-end audio-clock split, as m10-16) with
the flip control flagged = sim identical; a first mismatch at a tick with a different caller set = sim divergence, name it.
Then mission 19 (LEVEL 18). After that the per-mission G3 sweep is closed; next rung per ITERATION.md 3c.
