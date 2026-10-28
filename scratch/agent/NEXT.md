# NEXT: dd5 on large-terrain levels (lvl3 78x78, lvl7 93x96) — does dd>4 pay there?
HYPOTHESIS-ID: g1c-dd-phase2
State (s6584): lvl1/5/10 extent-bound at dd4 bundle (census 0 cap-trim). Bundle clamps px at 5.
Work unit: run lvl3 and lvl7 at ROGUESQ_DRAW_DISTANCE=4 and 6 (one at a time, ROGUESQ_DD_LOG=1, 150 s, recipe like scratch/agent/s6582_run.sh with MISSION_RE for that level), compare post-window area and cap-trim count, and 300 s clean hold at the winning dd.
Outcomes: cap-trim 0 and area grows 4->6 => raise bundle px cap beyond 5 for these levels; cap-trim >0 at dd6 => px cap (5) is the binding limit, raise it; area flat => extent-bound everywhere, close G1c phase 2 and hand owner the dd4 sheet.
