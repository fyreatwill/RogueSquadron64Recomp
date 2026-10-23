# NEXT: G4 crash/stall hunting — queue 3x 660 s holds on lvl0 (only lvl1-9 have 660 s holds) via soak_queue, fold verdicts
HYPOTHESIS-ID: g4-crash-stall-hunt
H: (a) lvl0 holds clean 660 s (b) a distinct crash/stall exists. Discriminator: 3 runs, 0 crash/0 VI stall = clean; any abort -> lldb backtrace. Copy recipe from soak_queue/done/m6_lvl1_hold660_r1_*.sh with lvl0 route (see g1_lvl0_oracle_pair_*.sh).
