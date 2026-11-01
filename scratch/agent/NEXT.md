# NEXT: G3 -- mission 6 (The Jade Moon) in-flight sim/frame match with dt pinned (s6753-s6756 method)
HYPOTHESIS-ID: g3-mission6-pinned

s6756 closed lvl5: H-match for all 1972 retail ticks (20635 rand calls, NPC state, event mask, song handle) and 17/20
frames (outliers = retail mid-draw dumps). Recipes: scratch/s6757/retail.sh, port.sh (spec + AI rows + fb dumps built in).
g3_rand_ticks.py / g3_rand_align.py now skip the AI marker rows.

Work (runs in scratch/s6758; one game run at a time):
1. `python3 tools/g3_eep_patch.py scratch/s6754/lvl4.eep scratch/s6758/lvl6.eep --set 0x31=5`
2. Copy scratch/s6757/retail.sh and port.sh, sed s6757->s6758 and lvl5->lvl6. Retail SECS=260 (lvl5 retail ran ~3 VI per
   tick, so 200 s gave only 1972 ticks); port SECS=150. Check retail tick 0 VI vs --fb-arm-after 103 (lvl6 intro may be
   longer: if tick 0 is past ~110 s, raise FARM).
3. Analyse: g3_rand_ticks.py RETAIL PORT; g3_frame_snap.py RETAIL PORT <retail ticks> (only clock words 3-6/9 and glob
   20-31 may differ); G3_IGN=04,0c,18 g3_tick_mem.py RETAIL PORT 8010c9e0 8010c0e0; g3_ai_clock.py; g3_oracle_match.py
   --w 512 --bases 690000,620000 --h 446 --win 60,1024 --winx 85,1191 --dec shift --worst 3 (view worst sheets).
Outcomes: identical up to an audio-clocked event = H-match (time it in AI buffers); a non-audio divergence = real port
defect -> bisect with xtrace-mem as s6751-s6753.
Positive control: the s6754 pair through g3_rand_ticks.py -> mismatch at index 2153.
