# NEXT: G3 dt-pinned sim + render match, mission 13
HYPOTHESIS-ID: g3-mission13-pinned

s6765 closed mission 12 (Escape from Fest): sim identical through t1006, split t1007 = song-1 end on the audio clock, and
pre-split render d<=9.3 (bolt phase only). Work unit (scratch/s6766), retail + port run concurrently:
1. eep: python3 tools/g3_eep_patch.py scratch/s6765/lvl12.eep scratch/s6766/lvl13.eep --set 0x31=12. Look at one port
   capture to confirm a new level. If it does not reach one, try ROGUESQ_FORCE_PLANET_UNLOCK=0xFF (port) and check retail.
2. for f in retail port; do sed 's/s6765/s6766/g; s/lvl12/lvl13/g; s/0x31=11/0x31=12/' scratch/s6765/$f.sh > scratch/s6766/$f.sh; done.
   Run `env SECS=360 NDUMP=24 DSTEP=10 zsh scratch/s6766/retail.sh` in the background and
   `env SECS=330 zsh scratch/s6766/port.sh` in the foreground. Grep port/run.log for `[ucode-cap] fired` and crash lines.
3. Offline: g3_rand_ticks, g3_song_windows, g3_frame_snap <ticks>, g3_tick_mem (G3_IGN=04,0c,18) 8010c9e0 8010c0e0,
   g3_oracle_match (--w 512 --bases 690000,620000 --h 446 --win 60,1024 --winx 85,1191 --dec shift --worst 6),
   g3_hud_presence scratch/s6766. Map dump VI to retail tick through snap.txt (field 5 = "Rvi/Pvi"). Torn retail
   dumps and post-split dumps are not defects. Check any port HUD-off window in a capture (death cam/debrief?).
4. Any port-only HUD-off window before the split: dense retail arm (scratch/s6763/lvl9_retail_gap2.sh pattern).
Discriminating outcomes: sim identical (to an audio-clocked split, or none) vs a new sim split (name the caller at the
first rand mismatch and the first tick_mem diff); render d<=~9 on pre-split dumps vs a port-only render defect.
