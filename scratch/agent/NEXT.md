# NEXT: G3 dt-pinned sim + render match, mission 14
HYPOTHESIS-ID: g3-mission14-pinned

s6766 closed mission 13: sim identical over the whole 4417-tick retail trace (no split), render match, HUD-off t4308+ =
in-mission cutscene. The retail exec trace hits its 400000 cap at ~t4417 (pass a larger --exec-trace count if a level
needs more). Work unit (scratch/s6767), retail + port run concurrently:
1. eep: python3 tools/g3_eep_patch.py scratch/s6766/lvl13.eep scratch/s6767/lvl14.eep --set 0x31=13. Look at one port
   capture to confirm a new level. If it does not reach one, try ROGUESQ_FORCE_PLANET_UNLOCK=0xFF (port) and check retail.
2. for f in retail port; do sed 's/s6766/s6767/g; s/lvl13/lvl14/g; s/0x31=12/0x31=13/' scratch/s6766/$f.sh > scratch/s6767/$f.sh; done.
   Run `env SECS=360 NDUMP=24 DSTEP=10 zsh scratch/s6767/retail.sh` in the background and
   `env SECS=330 zsh scratch/s6767/port.sh` in the foreground. Grep port/run.log for `[ucode-cap] fired` and crash lines.
3. Offline: g3_rand_ticks, g3_song_windows, g3_frame_snap <ticks> > snap.txt, g3_tick_mem (G3_IGN=04,0c,18) 8010c9e0 8010c0e0,
   g3_oracle_match (--w 512 --bases 690000,620000 --h 446 --win 60,1024 --winx 85,1191 --dec shift --worst 6),
   g3_hud_presence scratch/s6767. Map dump VI to retail tick through snap.txt (field 5 = "Rvi/Pvi"). Torn retail
   dumps, post-split and post-trace-end dumps are not defects. Positive control: flip one mid-stream port rand value in a
   /tmp copy and confirm g3_rand_ticks flags it (s6766 recipe).
4. Any port-only HUD-off window before the split: dense retail arm (scratch/s6763/lvl9_retail_gap2.sh pattern).
Discriminating outcomes: sim identical (to an audio-clocked split, or none) vs a new sim split (name the caller at the
first rand mismatch and the first tick_mem diff); render d<=~9 on pre-split dumps vs a port-only render defect.
