# NEXT (s7622)
HYPOTHESIS-ID: g6-upstream-features

G6c step 2 per docs/G6C-STANDINS-PLAN.md: implement the stand-in hook, opt-in ROGUESQ_STANDINS=1, only at dd>1.
1. Decide the host region first (one code read + one check): does setupCameraMatrices / convertMat3x4ToN64Mtx 0x80018DEC copy an
   instance node's matrix into the DL pool (-> region may sit above 0x81000000: carve spill top 0x81700000..0x81800000, spill cap
   7 MB when STANDINS on, add arena to tools/s7336_host_arena_table.py) or emit a pointer to it (-> carve DL-pool bottom).
2. src/main/rs64_standins.cpp (upstream logic minus snapshot/replay/probe droid; dd from ROGUESQ_DRAW_DISTANCE) +
   tools/apply_s7622_standins.py inserting the call after `L_800FAC68:` in runInMissionFrame, appended to RS64_REPLAY.
   Regen order: make_elf.py -> N64Recomp -> fixup_game_funcs.py -> cmake.
3. One run, L1 dd2 forced level: positive control `[standins] N objects` N>0 and per-second submitted count >0; same build dd1
   arm: 0 submits. Log bucket fill and spill peak. Outcomes: N=0 -> data addresses differ (re-derive from our syms);
   N>0 but submitted 0 -> grid/condition gates differ; submitted>0 -> step 3 (tog on/off frames dd2/dd4, 2 levels).
Hygiene: one game at a time; never touch build/saves or clear ROGUESQ_NO_SAVE_WRITE; never launch under lldb.
