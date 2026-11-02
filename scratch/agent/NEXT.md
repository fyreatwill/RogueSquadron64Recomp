# NEXT: G3 dt-pinned sim + render match, mission 11
HYPOTHESIS-ID: g3-mission11-pinned

s6763 closed mission 10 (sim identical 1410 ticks, split = song-1 end on the audio clock, render/HUD match) and the
lvl9 second HUD gap (retail death camera). Work unit (scratch/s6764), retail + port concurrently:
1. eep: python3 tools/g3_eep_patch.py scratch/s6763/lvl10.eep scratch/s6764/lvl11.eep --set 0x31=10. If the port does not
   reach a new level (look at one capture), try ROGUESQ_FORCE_PLANET_UNLOCK=0xFF on the port arm only and check retail too.
2. sed scratch/s6763/{retail,port}.sh s6763->s6764 and lvl10.eep->lvl11.eep. Run
   `env SECS=360 NDUMP=24 DSTEP=10 zsh scratch/s6764/retail.sh` in the background and `env SECS=330 zsh scratch/s6764/port.sh`
   in the foreground; then grep run.log for `[ucode-cap] fired` (expect 0) and crash lines.
3. Offline: g3_rand_ticks, g3_song_windows, g3_frame_snap <split-1>, g3_tick_mem (G3_IGN=04,0c,18) 8010c9e0 8010c0e0,
   g3_oracle_match (--w 512 --bases 690000,620000 --h 446 --win 60,1024 --winx 85,1191 --dec shift [--worst 6]),
   g3_hud_presence scratch/s6764. Look at the worst pairs: torn retail dumps (mid-raster stripes) are not defects.
4. Any port-only HUD-off window: aim a dense retail arm at it (scratch/s6763/lvl9_retail_gap2.sh pattern, DOFF seconds
   after the flight-start arm at ~60 VI/s) and read the census shape (tris up + texrects 0 = truncation; tris down = scene).
Discriminating outcomes: sim identical up to an audio-clocked split (known) vs a new sim split (name the caller at the
first rand mismatch and the first tick_mem diff); render d<=7 on pre-split dumps vs a port-only render defect.
