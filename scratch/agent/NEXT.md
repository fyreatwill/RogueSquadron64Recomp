# NEXT: fold m6_lvl{11,12,13,14,16,17,18}_hold660 verdicts (G4); then (c) framebuffer check for lvl10-18
HYPOTHESIS-ID: g4-crash-stall-hunt
s6001: lvl0 r3 clean (lvl0 G4 closed). The "white pillar stubs" Next items (s5964/s5970/s5999) are STALE: s5971 found the writer (ROGUESQ_FIX_ZERO_SHADE), default OFF, verified on all 9 levels. Queued 660 s holds for lvl 11-14,16-18 (10/15 need ~790 s viewer wait; do separately with SOAK_TIMEOUT~2100).
Any abort -> lldb/ASan backtrace, name the writer. If clean, view fbd last frames for lvl10-18 (terrain/craft/HUD) = G1(c).
