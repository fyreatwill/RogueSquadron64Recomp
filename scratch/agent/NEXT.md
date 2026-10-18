# Next work unit: fold m6_keyed_ap_{a,b,c} results; fix each DISTINCT failure at the root
HYPOTHESIS-ID: m6-mission-endurance

s5416 solved key delivery (autopilot; winctl keys can't reach SDL because the game is never frontmost). Read SOAK-RESULTS.md for m6_keyed_ap_*; check keys.log in scratch/agent/m6/s5416_soak_*/ and the frame-hash (fbhash) metric to confirm a real mission, not attract. For each distinct CRASH/stall: lldb or ASan backtrace, name the writer, root-cause fix (no guard-one-deref). If all 3 hold clean 480 s, extend the hold to 1200 s and add a frozen-frame check.
