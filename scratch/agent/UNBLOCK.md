# UNBLOCK s5053
Route taken: 3 (re-scope). Routes 1-2 failed.
Route 1 (refute): the H1-vs-H3 test needs the game to reach hangar via synthetic keys; no offline route gives the same answer, and no older known-good binary is retained as a same-host control.
Route 2 (satisfy locally): needs load <2. Measured 17:07 load 6.41/5.58/5.43: Chrome Helper 109%, WindowServer 41%, bluetoothd 26%, REAPER 20%. Lowering it means quitting the user's apps, which is a human decision.
Route 3: NEXT.md rewritten to an offline, game-free unit; open dependency recorded in CURRENT-TRUTH. BLOCKED.md removed because the loop can continue on work that doesn't need a quiet host.
Observation that would refute my conclusion: load average <2 for a run of scratch/agent/s5048_preS5038_source.sh (hangar => H1, nohangar => H3).
