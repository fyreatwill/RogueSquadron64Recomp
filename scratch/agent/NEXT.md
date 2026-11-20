# NEXT (s7699)
HYPOTHESIS-ID: post-g6c-owner-wait-s7699

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report.
State: s7698 re-held the s6908 intro pool floor on the post-G6c binary (same-run POOLMIN_TOG: kept nodes 3024/2014 L1 dd4, 1226/897 L4 dd2;
pixels move on L4 dd2 only). Every ladder rung is closed or waiting on the owner (CURRENT-TRUTH Next steps 2-9, 20, 22).
Step 0: CURRENT-TRUTH ~59.5 KB; if > 60000, maintenance (migrate s7660-s7698 headline + G6c detail to PROJECT-OVERVIEW).
Otherwise pick the first open rung not waiting on the owner; every iteration must land a datum or a code change.
Candidate: same re-hold for the other s6908-s6919 G5h levers at dd4 on L5 (`env LV=5 DD=4 zsh tools/s7698_poolmin_rehold.zsh`, then
tools/s7698_kept_split.py / s7698_flip_pairs.py scratch/s7698/L5d4 5): expected kept split floor>old; pixel split either way (L1-like = invisible).
