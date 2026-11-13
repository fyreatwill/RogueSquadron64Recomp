# NEXT (s7248): does the WIDEWIN stack (R48 + MERGE0.4 E16) restore 60/s in the L4 heavy window? Fixed-on, no tog
HYPOTHESIS-ID: widewin-heavy-window-cost
State (s7247): same-run tog says the stack cuts window gfx work -3.63/-3.88 ms (r48 alone -3.72/-2.83, E16 alone -1.33/-1.35), no seams, no holes
(tools/s7247_tog_pop.py, control PASS). s7231 fixed arms: dd4 13.96 ms/60 fps, dd4+WW 18.47 ms/30 flat. Tog arms cannot show fps (phase mix).
Work unit: ONE soak, 3 arms x 2 runs, fixed settings (no _TOG), owner idle >= 180 s, screen unlocked. Copy scratch/s7247/s7247_stack_timing.sh to
scratch/s7248/, drop every *_TOG, arms: off (WIDEWIN=0), ww (WIDEWIN=1), stack (WIDEWIN=1 + R=48 + MERGE=0.4 + MERGE_E=16); then repeat the arms
(offb wwb stackb). Score: window t=77-97 and flight 60-230 fps (fl_shown / present ring, tools/s7229_flat30_cost.py for flat-30 runs) and gfx task ms
(tools/s7230_headroom.py). Positive control: the ww arm must reproduce s7231's flat-30 window (else the route did not reach the heavy stretch).
Outcomes: H-60 (stack window >= 58 fps and no flat-30 run >= 2 s, both runs) -> OWNER-OPT-INS: drop "steady-60 unverified", ask the owner whether
WIDEWIN+stack should become part of the 21:9 auto bundle; H-30 (still flat 30) -> stack ms vs 16.7 says how much more is needed (next lever:
R=40 had -3.19 ms but -8.6% kpx; rescore it with the hole scorer); H-mixed -> report the distribution.
