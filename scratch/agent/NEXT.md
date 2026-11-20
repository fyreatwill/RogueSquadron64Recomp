# NEXT (s7701)
HYPOTHESIS-ID: post-g6c-owner-wait-s7701

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report.
State: the s6908 cutscene pool floor is re-held post-G6c on intros (L1/L4/L5, s7698/s7699) and the AT THE MOVIES playlist (s7700, dd2
visible, dd4 invisible). Every ladder rung is closed or waiting on the owner (CURRENT-TRUTH Next steps).
Step 0: CURRENT-TRUTH ~59.6 KB; maintenance triggers at > 60000. If it does, migrate the s7660-s7700 headline + G6c detail to
PROJECT-OVERVIEW and do nothing else.
Otherwise, candidate: the owner also plays 21:9. Re-hold the playlist at 21:9 dd2 (wider view = more ground needed):
  env DD=2 AS=21:9 GW=2048 O=$PWD/scratch/s7701/mov219d2 zsh tools/s7700_poolmin_movies.zsh
  then LV=-1: tools/s7698_kept_split.py, s7698_flip_pairs.py, s7699_arm_sheet.py <dir> -1 <png> 6 --nocut (view the sheet).
Outcomes: H-holds (holes in old-cap frames, filled by the floor) / H-short (floor 4096 itself leaves holes at 21:9: the window p50 sits at
the 4096 cap -> propose a higher floor at 21:9) / H-invisible. Check the 21:9 menu gate reached the playlist (`-> 4096` poolx lines).
