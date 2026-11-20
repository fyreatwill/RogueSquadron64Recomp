# NEXT (s7697)
HYPOTHESIS-ID: post-g6c-owner-wait-s7697

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report.
Fold: soaks s7696_cut_L1 / s7696_cut_L4 (queued). Expect tag lines `pre_in_cine=0 flight_secs_ge50>10 alive=1 crash=0`
(H-absent replicate: stand-ins hook gets 0 calls in the intro cutscene). If pre_in_cine>0 on a level, that level's intro runs the
mission frame: rerun tools/s7696_cut_standins.zsh with LV=<n> DUMP=c2:8:40 and score pairs with tools/s7628_standins_sheet.py.
If cine_line=0, the level's intro was not reached via cineBody (check the route screenshots), not a refutation.
State: s7696 selected H-absent on L5 (census gap + fb-dump ordering, flight control 57-62 calls/s, sheet med_fpx 79 PASS).
Every ladder rung is closed or waiting on the owner (CURRENT-TRUTH Next steps 2-9, 20, 22). Step 0: CURRENT-TRUTH ~58.8 KB; if > 60000,
maintenance (migrate s7660-s7692 G6c detail in Next steps item 20 to PROJECT-OVERVIEW).
Otherwise pick the first open rung not waiting on the owner; every iteration must land a datum or a code change.
