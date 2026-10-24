# NEXT: G1c - fold s6065_px2_dd2_hold300_l5 / l10, then terrain fraction for fixed-dd runs
HYPOTHESIS-ID: g1c-heap-exhaustion
Level 1 px2 dd2 300 s hold is clean (s6066). Fold SOAK-RESULTS lines for s6065_px2_dd2_hold300_l5 and _l10 (check rc, crashlines, vi_stalls30s, post-'cap 2048' '[heaplog].*-> 00000000').
Both clean -> G1c crash criterion met; ask owner to judge look. Then measure terrain fraction dd1 vs dd2 using the metric() in tools/g1c_ddtog_fold.py on fixed-dd fb dumps (the fold tool itself needs [ddtog] runs). Any crash -> backtrace it.
