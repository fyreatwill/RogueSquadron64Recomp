# NEXT (s5916): per-window class-1 crossing tally, offline on s5915_steer/run.log

HYPOTHESIS-ID: g1-mission-progression

s5915: run with ROGUESQ_NO_CRASH=1 survived 412 s with all stick windows logged (418 plpos rows, 50197 s5901 rows).
Work unit (offline, no game run): join [s5901] rows to el windows via cycle/plpos order; per window (A-only 130-227, sua/sra/sda/sla from 230 in 30 s steps) count rows with c1f=1 and best_ratio<=1.
Control: A-only window. Positive control: each window has nonzero plpos movement.
Outcomes: crossings rise in a stick window vs A-only -> aim confirmed, build closed-loop steering; flat -> steer direction not toward NPCs, compute bearing from the player dump.
