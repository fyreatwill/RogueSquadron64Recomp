# NEXT: G3 dt-pinned sim + render match, mission 12
HYPOTHESIS-ID: g3-mission12-pinned

s6764 closed mission 11 (Bespin): sim identical for the whole 3410-tick retail trace (78 NPCs, no split, no song switch),
render d 4.9-7.1, HUD on in both arms. Work unit (scratch/s6765), retail + port concurrently:
1. eep: python3 tools/g3_eep_patch.py scratch/s6764/lvl11.eep scratch/s6765/lvl12.eep --set 0x31=11. Look at one port
   capture to confirm a new level; if it does not reach one, try ROGUESQ_FORCE_PLANET_UNLOCK=0xFF (port) and check retail.
2. for f in retail port; do sed 's/s6764/s6765/g; s/lvl11/lvl12/g' scratch/s6764/$f.sh > scratch/s6765/$f.sh; done.
   Run `env SECS=360 NDUMP=24 DSTEP=10 zsh scratch/s6765/retail.sh` in the background and
   `env SECS=330 zsh scratch/s6765/port.sh` in the foreground; grep port/run.log for `[ucode-cap] fired` and crash lines.
3. Offline: g3_rand_ticks, g3_song_windows, g3_frame_snap <ticks>, g3_tick_mem (G3_IGN=04,0c,18) 8010c9e0 8010c0e0,
   g3_oracle_match (--w 512 --bases 690000,620000 --h 446 --win 60,1024 --winx 85,1191 --dec shift --worst 6),
   g3_hud_presence scratch/s6765. Torn retail dumps (mid-raster stripes) are not defects.
4. Any port-only HUD-off window: dense retail arm (scratch/s6763/lvl9_retail_gap2.sh pattern).
Discriminating outcomes: sim identical (to an audio-clocked split, or none) vs a new sim split (name the caller at the
first rand mismatch and the first tick_mem diff); render d<=7 on pre-split dumps vs a port-only render defect.
