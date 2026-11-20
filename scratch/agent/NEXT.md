# NEXT (s7698)
HYPOTHESIS-ID: post-g6c-owner-wait-s7698

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report.
State: s7697 folded s7696_cut_L1/L4 — H-absent (stand-ins get 0 calls in mission intro cutscenes) holds on L1/L4/L5. Soak verdicts
now read alive=/crash= aliases and end with alive_na=; when folding, alive=0/k with alive_na=k means "recipe has no alive key", not dead.
Every ladder rung is closed or waiting on the owner (CURRENT-TRUTH Next steps 2-9, 20, 22). Step 0: CURRENT-TRUTH ~59.3 KB; if > 60000,
maintenance (migrate s7660-s7696 G6c detail in Next steps item 20 + headline s7690-s7697 to PROJECT-OVERVIEW).
Otherwise pick the first open rung not waiting on the owner; every iteration must land a datum or a code change.
Candidate: G5h — the intro cutscene background loss at dd4 is NOT stand-ins (s7696/s7697); count missing ground/water per
intro at dd2/dd4 vs dd1 on L1/L4 with the existing cutscene dump route (tools/s7696_cut_standins.zsh, ROGUESQ_STANDINS=0).
