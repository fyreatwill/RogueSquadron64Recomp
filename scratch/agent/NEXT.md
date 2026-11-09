# NEXT: G1c per-cell cost — split streamTerrainGridCellsByDistance's 171 ns/cell into loop self vs callees, and count the skip path
HYPOTHESIS-ID: g1c-dd-headroom
Context (s7022, ROGUESQ_S7022_ST=1, same-run tog3 8192/10240, L1 dd6 21:9 WIDEWIN owner path): the walk is linear, once per frame,
1.38 ms at 8192 cells / 1.69 ms at 10240, 171 ns/cell inclusive; setup 0.5 us. Do NOT use xctrace per-line splits inside this function
(62% of samples land on 0.5 us of setup code: attribution artifact).
G5i: fixed, owner look only — check CURRENT-TRUTH item 1 first.
Hypotheses:
 H-callee: most of the 171 ns is inside getGridCellValueAt / processGridCellByDistance (called per passing cell) -> optimise or host-index them
   (s6963 cellidx precedent: answer a chain walk from a host index).
 H-self: the loop's own per-cell code (recomp ctx traffic + the s6513/s6526/s6515/s6588/s6038 diagnostic hooks + g_s6493 increments) is most
   of it -> strip/gate the diagnostic hooks to one predictable branch, measure.
 H-skipmix: cells mostly take the span-equal skip (g_s6493[4]) and are cheap; a minority pass and are expensive -> change detection could skip
   passing cells whose span did not change since last frame.
Discriminator, ONE build, ONE run (same recipe scratch/s7022/run.zsh): extend tools/apply_s7022_streamtime.py so rs64_s7022_st also gets
(a) mach time spent inside the two callee calls (accumulate around each call site in the loop), (b) per-call counts of skip-path cells,
call-path cells, and range-reject cells. Report per cap: self ns/cell, callee ns/call, fraction per path. Outcome: callee share >60% ->
H-callee; self >60% -> H-self (then a same-run tog that bypasses the diag hooks: ROGUESQ_S7022_NODIAG=tog); pass fraction small but
callee cost dominant -> H-skipmix. Then one change with a same-run tog A/B (xor8 split).
Summarise with: python3 tools/s7022_streamtime_sum.py scratch/agent/m6/g1_lvl1s7022S6/run.log 6 (rename tag per run).
