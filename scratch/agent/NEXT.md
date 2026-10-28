# NEXT: G3c (owner visual defects) — start with (a) jagged far-terrain edge arm table
HYPOTHESIS-ID: g3c-visual-defects
State (s6543): cap thread closed enough: cap120 ~= cap0 terrain, only inf buys terrain (~3x) at ~1.7x wall. Leave the default; owner question in CURRENT-TRUTH s6543 line (cap0 vs inf for dd>1). Optional later: cap knee 300/600 via CAP_ALT.
Work unit: G3c(a). Arm table (retail, DD=2, DD=4 default cap, DD=4 inf, ASPECT alone) at a pinned pose (s6542_run.sh recipe), score the far-terrain edge (tools/g3c_edge_score.py exists), root-cause the stair-step, produce before/after frames. Read CURRENT-TRUTH G3c(a) notes (height-byte fade was null, s6389).
Outcome logic: retail shows no edge -> opt-in owns it (which one splits via arms); edge in retail too -> not a regression.
