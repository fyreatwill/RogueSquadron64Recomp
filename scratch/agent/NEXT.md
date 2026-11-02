# NEXT: G3 dt-pinned sim + render match, mission 15
HYPOTHESIS-ID: g3-mission15-pinned

s6767 closed mission 14 (lava planet): sim identical 2875 ticks, split = song-1 end on the audio clock, render d 1.8-4.2
pre-split, port HUD-off t2628-2865 = in-mission cutscene (retail dump inside is HUD-off too). Work unit (scratch/s6768),
retail + port run concurrently:
1. eep: python3 tools/g3_eep_patch.py scratch/s6767/lvl14.eep scratch/s6768/lvl15.eep --set 0x31=14. Look at one port
   capture to confirm a new level. If it does not reach one, try ROGUESQ_FORCE_PLANET_UNLOCK=0xFF (port; CURRENT-TRUTH
   says lvl15 needs it) via EXTRA= and check retail reaches it too.
2. for f in retail port; do sed 's/s6767/s6768/g; s/lvl14/lvl15/g; s/0x31=13/0x31=14/' scratch/s6767/$f.sh > scratch/s6768/$f.sh; done.
   Run `env SECS=360 NDUMP=24 DSTEP=10 zsh scratch/s6768/retail.sh > scratch/s6768/retail_run.txt 2>&1 &` and
   `env SECS=330 zsh scratch/s6768/port.sh` in the foreground. Grep port/run.log for `[ucode-cap] fired` and crash lines.
3. Offline (cwd = repo root; g3_oracle_match needs it for the dump paths): g3_rand_ticks, g3_song_windows,
   g3_frame_snap <split tick> > snap.txt, g3_tick_mem (G3_IGN=04,0c,18) 8010c9e0 8010c0e0,
   g3_oracle_match (--w 512 --bases 690000,620000 --h 446 --win 60,1024 --winx 85,1191 --dec shift --worst 6),
   g3_hud_presence scratch/s6768. The oracle_match port index is a free search: for an outlier, map retail vi -> tick
   via snap.txt and view the port capture at (port vi/60 + t0). Torn retail dumps, post-split and post-trace-end dumps
   are not defects. Positive control: flip rand index 20000 in a /tmp copy (s6767 python snippet in PORTING-STATE) and
   confirm g3_rand_ticks reports index 20000.
4. Any port-only HUD-off window before the split: dense retail arm (scratch/s6763/lvl9_retail_gap2.sh pattern).
Discriminating outcomes: sim identical (to an audio-clocked split, or none) vs a new sim split (name the caller at the
first rand mismatch and the first tick_mem diff); render d<=~9 on pre-split dumps vs a port-only render defect.
