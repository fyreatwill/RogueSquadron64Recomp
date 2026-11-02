# NEXT: G3 dt-pinned sim + render match, mission 16
HYPOTHESIS-ID: g3-mission16-pinned

s6768 closed mission 15 (canyon/bunkers, X-wing): sim identical 1377 ticks, split t1378 = song-1 end on the audio clock,
render d 5.0-8.5 pre-split (vi 7930/9730 torn retail dumps), port HUD-off t1082-1379 = overhead cutscene, retail inside
HUD-off too. Work unit (scratch/s6769), retail + port run concurrently:
1. eep: python3 tools/g3_eep_patch.py scratch/s6768/lvl15.eep scratch/s6769/lvl16.eep --set 0x31=15. Look at one port
   capture to confirm a new level (s6768 = grey sky, rocky canyon, bunkers, X-wing).
2. for f in retail port; do sed 's/s6768/s6769/g; s/lvl15/lvl16/g; s/0x31=14/0x31=15/' scratch/s6768/$f.sh > scratch/s6769/$f.sh; done.
   Run `(env SECS=360 NDUMP=24 DSTEP=10 zsh scratch/s6769/retail.sh > scratch/s6769/retail_run.txt 2>&1 &)` and
   `env SECS=330 zsh scratch/s6769/port.sh > scratch/s6769/port_run.txt 2>&1` in the foreground. Retail finishes ~450 s
   after start; wait with `pgrep -x rs64_oracle` (NOT pgrep -f: it matches the waiting shell itself).
   Grep port/run.log for `[ucode-cap] fired` and crash lines.
3. Offline (cwd = repo root): g3_rand_ticks, g3_song_windows, g3_frame_snap R P <split tick+6> > snap.txt,
   g3_tick_mem (G3_IGN=04,0c,18) 8010c9e0 8010c0e0, g3_oracle_match (--w 512 --bases 690000,620000 --h 446
   --win 60,1024 --winx 85,1191 --dec shift --worst 6) > match.txt, g3_hud_presence scratch/s6769. Port n in match.txt =
   capture seconds*100; map a retail vi to a tick via snap.txt (`tick N ... vi R/P`), port capture ~ P/60 s. Parse
   snap.txt for the first obj diff / disallowed word with the s6768 python pass (PORTING-STATE s6768). Torn retail
   dumps, post-split dumps are not defects. Positive control: python3 scratch/s6768/flip_ctl.py <port.rand> /tmp/x 20000,
   then g3_rand_ticks must flag the flipped value.
4. Any port-only HUD-off window before the split: dense retail arm (scratch/s6763/lvl9_retail_gap2.sh pattern).
Discriminating outcomes: sim identical (to an audio-clocked split, or none) vs a new sim split (name the caller at the
first rand mismatch and the first tick_mem diff); render d<=~9 on pre-split dumps vs a port-only render defect.
