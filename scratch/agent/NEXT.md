# NEXT: fold m6_lvl18_hold660 (G4), then close G4 0-18 and move to G3
HYPOTHESIS-ID: g4-crash-stall-hunt
s6005: lvl16/17 holds clean (fail-retry cycles, no crash/stall). Fold lvl18 from SOAK-RESULTS.md (grep mission_cycles in its log). If clean, G4 is closed 0-18: take G3 (hangar artifacts in CURRENT-TRUTH, or in-flight frame diff vs retail oracle pair g1_lvl0_oracle_pair). Any abort -> lldb/ASan backtrace, name the writer.
