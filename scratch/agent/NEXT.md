# NEXT: G3 dt-pinned sim + render match, mission 10
HYPOTHESIS-ID: g3-mission10-pinned

s6762 closed g3-lvl9-hud-drop: the LLE ucode iteration cap (16384) truncated dense dd1 frames; default is now 65536.
Work unit (scratch/s6763), retail + port concurrently, as s6761:
1. eep: cp scratch/s6761/lvl9.eep -> lvl10.eep and set +0x31=9 (tools/g3_eep_patch.py). lvl10 may need
   ROGUESQ_FORCE_PLANET_UNLOCK=0xFF on the port (CURRENT-TRUTH run recipes); check the retail level name in a dump.
2. Copy scratch/s6762/{retail,port}.sh with dir s6763 and the new eep; retail SECS=360, port SECS=330; keep
   ROGUESQ_G3_CENSUS on the port (cheap now) and grep run.log for `[ucode-cap] fired` (expect 0).
3. Offline: g3_rand_ticks, g3_frame_snap, g3_song_windows, g3_oracle_match, g3_hud_presence.
Discriminating outcomes: sim identical to the first split (pacing/audio clock = known mechanism) vs a new sim split
(name the caller at the first rand mismatch); any port-only HUD-off window -> census says built-but-absent or not built.
Side check: also rerun the lvl9 port arm (scratch/s6762/port.sh SECS=330) and confirm ticks 2054-2208 now show the HUD.
