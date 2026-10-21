# NEXT: G1 — fold s5790_wr_fire / s5790_wr_nofire soak results (SOAK-RESULTS.md, logs in scratch/agent/soak_results/)
Grep logs for `\[objwr\]|\[objcount\] get id=2`; order them. Candidate whose [objwr] line immediately precedes each id=2 val 1->2->3 step = writer; then read its condition (why friendly/loss objects count). Controls: both line kinds present, and fire vs nofire both show rise.
If no [objwr] line precedes the steps: writer is bulk copy/script; add a store watch on rdram 0x138064 (host-side) and re-queue.
HYPOTHESIS-ID: g1-mission-progression
