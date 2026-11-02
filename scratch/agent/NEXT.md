# NEXT: G3 bonus mission 19 (LEVEL 18) — sim/frame match with the s6772 cursor recipe
HYPOTHESIS-ID: g3-mission19-pinned

s6772 closed mission 18 (Death Star trench, sim identical t0-t1097, song-3 audio-clock split t1098). The game clamps
save +0x31 to 16, so mission 19 = cursor 18 = TWO d-pad RIGHT presses on the SELECT LEVEL screen (lvsel state 2).
Unknowns: whether mission 19 has a craft-select screen (m18 did, m17 did not), its name, its length unsteered.
Work unit:
1. Port probe (~100 s): env SAVE_FROM=scratch/s6772/lvl19.eep SECS=110 CAP0=26 \
     AP=6:start,11:start,16:start,21:start,23:w512,25:right,25.7:right,27:start,31:start,42:start \
     zsh tools/g3_port_capture.sh scratch/s6773/probe/p ; grep '[lvsel] tick' (cursor must reach 18, ret=0x12);
   contact sheet. Drop 42:start if there is no craft screen (a Start in flight pauses).
2. Retail timing probe only if needed (s6772/rp recipe: RS64_XTRACE_MEM=800C6674:0:800CDAC0:2,800FA730:29:10:10,
   --press ...,36:start,41:dright,42:dright,44:start,49:start,54:start[,64:start]); first 800fa730 xtrace = race start.
3. Paired: env G3_MIN_TICK=0 PRESS=<retail> AP=<port> DWARM=30 ARM=20 POKE=800FA730:29:30:3d088889,800FA730:0:80003470:1:1 \
     RSECS=260 PSECS=230 CAP0=58 NDUMP=40 DSTEP=4 FARM=<retail race start s +2> zsh tools/g3_mission/run.sh scratch/s6773/r19 18
   then env G3_MIN_TICK=0 G3_SNAP_TICKS=800FA730 zsh tools/g3_mission/offline.sh scratch/s6773/r19 (flip_ctl now starts at
   the first tick row, s6772 fix).
Discriminating outcomes: rand/NPC identical until a song-end audio-clock split (as m10-18) with the flip control flagged =
sim identical; a first mismatch at a tick with a different caller set before any song end = sim divergence, name it.
After mission 19 the per-mission G3 sweep is closed: take the next rung per ITERATION.md 3c (G1d owner close-out etc.).
