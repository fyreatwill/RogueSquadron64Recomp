# NEXT: G3 -- mission 7 in-flight sim/frame match with dt pinned (s6753-s6757 method)
HYPOTHESIS-ID: g3-mission7-pinned

s6757 closed lvl6 (Jade Moon): H-match for all 941 retail ticks (9438 rand calls, 12 NPCs, event mask) and 10/10 flight
frames (d 2.1-2.6). Only render-pacing words differ: snap word 2 (last-drawn tick, +-1 on 3 ticks) and glob word 18
(0x8011A8C8, buffer-arbiter slot bytes, 1 tick). Treat both as allowed in frame_snap from now on.
lvl6 intro was long: retail reached flight at VI 12912 (~215 s), so 260 s retail gave only 941 ticks; port at 150 s was
still in the intro (no rand trace) and needed SECS=330.

Work (runs in scratch/s6759; one game run at a time; CT is at 59.9 KB -> next iteration may be maintenance first):
1. `python3 tools/g3_eep_patch.py scratch/s6754/lvl4.eep scratch/s6759/lvl7.eep --set 0x31=6`
2. Copy scratch/s6758/retail.sh and port.sh, sed s6758->s6759, lvl6->lvl7, (+0x31=5)->(+0x31=6). Retail: `env SECS=360`
   (grep '[debug-write]' in retail/oracle.log for the flight VI; if absent the intro outran the run -> raise SECS).
   Port: `env SECS=330`; check port.rand.txt exists (it opens only at the first width-512 VI after ARM=55 s).
   lvl7 is the copyToRAM level fixed in s5712 - a crash here is a real datum.
3. Analyse: g3_rand_ticks.py RETAIL PORT; g3_frame_snap.py RETAIL PORT <retail ticks> (allowed: snap words 2-6/9, glob
   18 and 20-31); G3_IGN=04,0c,18 g3_tick_mem.py RETAIL PORT 8010c9e0 8010c0e0; g3_ai_clock.py RETAIL PORT;
   g3_oracle_match.py RETAIL scratch/s6759/port scratch/s6759/match --w 512 --bases 690000,620000 --h 446 --win 60,1024
   --winx 85,1191 --dec shift --worst 3 (view worst sheet).
Outcomes: identical up to an audio-clocked event = H-match; a non-audio divergence = real port defect -> bisect with
xtrace-mem as s6751-s6753.
Positive control: `g3_rand_ticks.py scratch/s6754/retail2/oracle.log scratch/s6754/port.rand.txt` -> mismatch at index
2153 (NOT scratch/s6754/retail/, which is a short run and reports None).
