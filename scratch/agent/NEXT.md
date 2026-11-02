# NEXT: G3 dt-pinned sim + render match, mission 17
HYPOTHESIS-ID: g3-mission17-pinned

s6769 closed mission 16 (ocean/Calamari towers): sim identical 2038 ticks, split t2039 = song-3 end on the audio clock,
render d 3.96-13.2 pre-split (vi 15145 torn retail; d 10-13 = capture phase), port HUD-off t1864-2039 = death camera,
retail inside HUD-off too. Missions 18/19 (+0x31=17/18) remain after this one. Work unit (scratch/s6770):
1. eep: python3 tools/g3_eep_patch.py scratch/s6769/lvl16.eep scratch/s6770/lvl17.eep --set 0x31=16. Look at one port
   capture to confirm a new level (s6769 = ocean, sandy islands, grey Calamari towers).
2. for f in retail port; do sed 's/s6769/s6770/g; s/lvl16/lvl17/g; s/0x31=15/0x31=16/' scratch/s6769/$f.sh > scratch/s6770/$f.sh; done.
   Run `(env SECS=360 NDUMP=24 DSTEP=10 zsh scratch/s6770/retail.sh > scratch/s6770/retail_run.txt 2>&1 &)` and
   `env SECS=330 zsh scratch/s6770/port.sh > scratch/s6770/port_run.txt 2>&1` in the foreground. Wait for retail with
   `pgrep -x rs64_oracle`. If mission start comes late (s6769: first dump t=234 s), fewer dumps land; fine.
   Grep port/run.log for `[ucode-cap] fired` and crash lines.
3. Offline (cwd = repo root): g3_rand_ticks, g3_song_windows, g3_frame_snap R P <split tick+6> > snap.txt then
   python3 scratch/s6769/snap_parse.py snap.txt, g3_tick_mem (G3_IGN=04,0c,18) 8010c9e0 8010c0e0, g3_oracle_match
   (--w 512 --bases 690000,620000 --h 446 --win 60,1024 --winx 85,1191 --dec shift --worst 6) > match.txt,
   g3_hud_presence scratch/s6770. Map retail vi -> tick via snap.txt rows; port capture ~ P/60 s. For d>9 pre-split
   pairs, strip the port captures +-1 s (s6769 strip_t971 pattern) before calling a defect: capture spacing is 0.33 s.
   Positive control: python3 scratch/s6769/flip_ctl.py <port.rand> /tmp/x 30000 (NOT the s6768 script), then
   g3_rand_ticks must flag the flipped value.
4. Any port-only HUD-off window before the split: dense retail arm (scratch/s6763/lvl9_retail_gap2.sh pattern).
Discriminating outcomes: sim identical (to an audio-clocked split, or none) vs a new sim split (name the caller at the
first rand mismatch and the first tick_mem diff); render d<=~9 on pre-split dumps vs a port-only render defect.
