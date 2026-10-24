# NEXT: G1c - find where dd breaks the frame, then name the truncator
HYPOTHESIS-ID: g1c-draw-distance
s6057: within-run dd1/dd2 toggle shows dd2 frames lose terrain AND HUD (86/200 HUD frames, terrain 0.02 vs 0.086); dd0.5 control behaves. Extra cells do not reach pixels; frame is broken at 2x.
1. Fold queued arms (loop runs them): s6057_ddtog125, s6057_ddtog15 -> `python3 tools/g1c_ddtog_fold.py scratch/agent/m6/g1_lvl1g1cddtog125 4500 --hud` (and ...15). Outcome splits: terrain GAIN with HUD intact at 1.25/1.5 => break point is between; use that as the supported max and keep digging above it. Already broken at 1.25 => truncation is not pool-cap bound, look at RSP DL/vertex/DMEM output buffers.
2. Name the truncator: at dd2 compare the DL length / final RSP task output (ROGUESQ_LOG_RDP_TRICOUNT is budget-capped to early ords; make a flight-phase-scoped counter) for blk0 vs blk1 frames in one toggle run. Candidates: pool cap u16 0x80130C4C (=2048, binds at 2x; try raising to 4096 in a toggle arm), DL buffer size, vertex buffer, RT64 draw limit.
3. Default stays retail. No macOS `timeout`. Dump rate var is FBD_EVERY_V.
