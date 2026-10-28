# NEXT: per-level terrain-extent census, then bundle dd knob and hold
HYPOTHESIS-ID: g1c-dd-phase2
Fact (s6576): lvl1 [ddclamp] post area hits 4096 (full 64x64 = level extent tw*th) by dd6; pre area keeps growing. So the limit on lvl1 is the level's extent, not a table.
Hypotheses: H-extent (all levels are extent-bound, dd~6 is the useful ceiling) vs H-cap (cap 0xC4C=2048 or tw/th>64 on some levels binds first) vs H-sample (60th-call sampling hides it).
Work unit: read tw/th/cap/post area for lvl5, lvl10 and 2-3 other levels from existing m6 logs (grep "[ddclamp]" dirs g1_lvl5*, g1_lvl10*; those with ROGUESQ_DD_LOG). Positive control: lvl1 reproduces 4096. If any level shows post area < tw*th at dd>=6 with cap binding => cap is the lever (raise cap, check heap). If all extent-bound => bundle far/pool/cap behind ROGUESQ_DRAW_DISTANCE, queue 300 s holds lvl1/5/10 at dd6, make dd1-vs-dd6 contact sheet for owner.
