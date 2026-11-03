# NEXT: G3 explosion under ROGUESQ_FPS60=1 vs retail (lvl14 cutscene destruction, t2737-2750)
HYPOTHESIS-ID: g3-explosion-fps60

State (s6812): the lvl14 cutscene vehicle destruction matches retail tick for tick at the default port rate
(scratch/s6812, tools/g3_tick_pair_score.py: median d 1.21 vs ctl 3.98). The owner plays with ROGUESQ_FPS60=1, which
changes the port VI/tick, so the s6767 snap.txt port-VI column no longer maps port frames to ticks.
Hypotheses: H-match (same sequence/colours per tick, only more frames); H-anim60 (effect animation stepped per render
frame instead of per sim tick at 60 Hz: dome expands twice as fast / ends early in ticks); H-blend60 (alpha/fade advanced
per frame -> darker/shorter dome).
Method: env EEP=scratch/s6767/lvl14.eep RSECS=276 FARM=255 NDUMP=192 DSTEP=0.08 PSECS=~150 CAP0=120 BURST=<t0>,<t1>
EXTRA=ROGUESQ_FPS60=1 zsh tools/g3_mission/fireball_pair.sh scratch/s6813/pair. FPS60 changes wall time per tick: first
locate the event from the port rand trace (scratch/s6813/pair/port.rand.txt) or rebuild snap.txt with g3_frame_snap.py
(s6767 recipe) for the new port VI column, and set BURST to cover t2700-2800 (do a short port-only scout if needed).
Score: g3_tick_pair_score.py with the NEW snap.txt; compare hot-pixel series per tick to s6812 retail rows.
Control: hot class fires on retail flash, 0 pre-event; cross-tick ctl vs paired d.
