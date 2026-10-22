# UNBLOCK (s5929) — route 3 (re-scope); route 1 attempted on paper, not run

Block: NEEDS-HUMAN physical — one human lv0 play via g1_human_play.sh (scratch/agent/m6/human1 does not exist; no human result on disk).
Route 1 (refute): the block is real as written (no yaw state, stick never moves xz => no automated control law). The one observation that would make it unnecessary: run the RETAIL ORACLE (rs64-oracle) under the identical scripted autopilot on lv0 (run_s3746_oracle_exact_route.sh / g1_* input schedule). If retail also never advances/kills class-1 NPCs, "autopilot never aims" is a tooling limit and G1 closes with no human. Not run this iteration (needs a game-run slot and oracle input plumbing check); recorded as NEXT step 1.
Route 2: nothing locally obtainable substitutes for a human flying a controller.
Route 3 (taken): G1 recorded as an open human dependency; NEXT.md rewritten to work that does not need it.
Route 4 not needed; BLOCKED.md removed because the loop can continue on the re-scoped unit (human question stays listed in CURRENT-TRUTH).
