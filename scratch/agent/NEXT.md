# NEXT: (1) Step-0 maintenance; (2) G3 mission 8 in-flight sim/frame match with dt pinned
HYPOTHESIS-ID: g3-mission8-pinned

CURRENT-TRUTH is 60.4 KB after s6758, so the next iteration is a MAINTENANCE iteration (Step 0): compact toward 35 KB,
migrate the FIXED G1d/G1e headline bullets (s6694-s6731) to PROJECT-OVERVIEW, merge the G3 per-mission bullets
(s6748-s6758) into one line, no experiments.

Then (iteration after): s6758 closed lvl7 up to the song end (tick 722 retail / 723 port, 640 AI buffers both arms).
Allowed render-pacing diffs in frame_snap: snap words 2-6/9, glob 7/8 (task/yield flag bytes), 18, 20-31.
Work (scratch/s6760; one game run at a time per arm; retail+port may run concurrently):
1. `python3 tools/g3_eep_patch.py scratch/s6754/lvl4.eep scratch/s6760/lvl8.eep --set 0x31=7`
2. Copy scratch/s6759/retail.sh and port.sh, sed s6759->s6760, lvl7->lvl8, (+0x31=6)->(+0x31=7). Retail `env SECS=360`,
   port `env SECS=330`. Note: do NOT wait with `pgrep -f 'rs64_oracle|g3_port_capture'` inside a shell whose own
   command line contains that pattern - it matches itself forever (s6758 lost 15 min). Wait on the PIDs instead.
3. Analyse exactly as s6758: g3_rand_ticks.py RETAIL PORT; g3_ai_clock.py RETAIL PORT (song end tick explains a split);
   g3_frame_snap.py RETAIL PORT <split tick-1>; G3_IGN=04,0c,18 g3_tick_mem.py RETAIL PORT 8010c9e0 8010c0e0;
   g3_oracle_match.py scratch/s6760/retail/oracle.log scratch/s6760/port scratch/s6760/match --w 512 --bases 690000,620000
   --h 446 --win 60,1024 --winx 85,1191 --dec shift --worst 3 (first arg is oracle.log, not the dir).
Outcomes: identical up to an audio-clocked event = H-match; a non-audio divergence = real port defect -> bisect with
xtrace-mem as s6751-s6753.
Positive control: `g3_rand_ticks.py scratch/s6754/retail2/oracle.log scratch/s6754/port.rand.txt` -> mismatch at 2153.
