# NEXT: G3 bonus mission 17 (Beggar's Canyon race) — tick key + fb arm, then the sim/frame match
HYPOTHESIS-ID: g3-mission17-pinned

s6770: missions 17-19 are bonus missions; save byte +0x39=0x60 unlocks them (tools/g3_mission/run.sh does it for
LEVEL>=16). Mission 17 is a race. Run scratch/s6770/m17b (PRESS to 36 s, DWARM=30, AP to 21 s, ARM=20) seeded both arms
but gave ticks=0 (race never calls runInMissionFrame 0x800FA730) and 0 retail fb dumps.
Work unit:
1. Offline first (no run): find the race's per-frame entry. The port census / run.log of scratch/s6770/m17b and the
   generated code (../N64Recomp/RecompiledFuncs) — the rand callers 0x800B0328/03A0/0F1C/0F48/09A8/0DB4 sit in 0x800B0xxx;
   walk their callers up to the function called once per sim frame in the race (compare how 0x800FA730 was found, s6754).
   Also read why rs64_oracle --fb-arm-after 103 never armed (grep fb-arm in tools/oracle source).
2. Make the tick key a parameter of the G3 tools (g3_rand_ticks/frame_snap/tick_mem/song_windows: env G3_TICK=<pc>) and of
   tools/g3_mission/run.sh (xtrace spec + --exec-trace-also), commit, re-run:
   env PRESS=6:start,11:start,16:start,21:start,26:start,31:start,36:start DWARM=30 AP=6:start,11:start,16:start,21:start \
     ARM=20 FARM=<fixed> G3_TICK=<pc> zsh tools/g3_mission/run.sh scratch/s6771 16
Discriminating outcomes: caller-order split at index 720 lands on one tick in both arms with a different caller set
(sim divergence: name the caller) vs lands on a pacing boundary (retail frame drop: same tick, different effect count) .
Then missions 18/19 (LEVEL 17/18) with the same tool.
