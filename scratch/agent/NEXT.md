# NEXT: G3 mission 9 in-flight sim/frame match with dt pinned
HYPOTHESIS-ID: g3-mission9-pinned

s6760 closed lvl8 up to the song-3 end (tick 1819 retail / 1850 port, the same 331-334 VI / 634-639 AI buffers in both).
Allowed render-pacing diffs in frame_snap: snap words 2-6/9, glob 7/8 (task/yield flag bytes), 18, 20-31.
Work (scratch/s6761; retail and port may run concurrently):
1. `python3 tools/g3_eep_patch.py scratch/s6754/lvl4.eep scratch/s6761/lvl9.eep --set 0x31=8`
2. Copy scratch/s6760/retail.sh and port.sh: sed s6760->s6761, lvl8->lvl9, (+0x31=7)->(+0x31=8). Retail `env SECS=360`,
   port `env SECS=330`. Wait on the PIDs (the retail.sh zsh PID and the g3_port_capture.sh PID), NOT with pgrep -f on a
   pattern your own wait command contains.
3. Analyse as s6760: g3_rand_ticks.py RETAIL PORT; g3_ai_clock.py RETAIL PORT (first song only);
   g3_song_windows.py RETAIL PORT (every song window: ticks/VI/AI buffers per arm);
   g3_frame_snap.py RETAIL PORT <split tick-1>; G3_IGN=04,0c,18 g3_tick_mem.py RETAIL PORT 8010c9e0 8010c0e0;
   g3_oracle_match.py scratch/s6761/retail/oracle.log scratch/s6761/port scratch/s6761/match --w 512 --bases 690000,620000
   --h 446 --win 60,1024 --winx 85,1191 --dec shift --worst 3. Look at the worst pngs: retail mid-draw dumps are common.
Hypotheses: H-match (identical up to an audio-clocked event or render-pacing words only) vs H-defect (a non-audio
divergence in rand/NPC/event state = real port defect -> bisect with xtrace-mem as s6751-s6753).
Positive control: `g3_rand_ticks.py scratch/s6754/retail2/oracle.log scratch/s6754/port.rand.txt` -> mismatch at 2153.
