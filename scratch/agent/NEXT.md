# NEXT: G1 — read s5787 soak verdicts: who increments objective counter 2 (fail at count >= 3)?

Fold SOAK-RESULTS lines s5787_cnt_fire / s5787_cnt_nofire. `grep -a '\[objcount\]' scratch/agent/soak_results/s5787_cnt_*.log | head -60`; backtraces follow the first id=2 lines.
- Control: any [objcount] line in each arm (else the instrument/route failed: recheck ROGUESQ_LOG_HUDBIT in XENV).
- H-friendly-loss: id=2 increments with ra in a mission script frame in both arms -> read the script's condition (friendly destroyed?) and find why friendlies die.
- H-ours: increments only in fire arm. H-port-bug: ra in a native handler (damage/collision) that should not fire.
Then name the guest caller (ra) via symbols and decide the fix.
HYPOTHESIS-ID: g1-mission-progression
