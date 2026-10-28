# NEXT: same-pose cap0 vs cap-inf frame pair (G1c phase 2)
HYPOTHESIS-ID: g1c-dd-phase2
State: s6545 sheet (docs/owner_sheet_s6545.png) is cross-run, poses differ -> not usable for the cap0/inf owner decision.
Work unit: reuse the s6542 same-run cap toggle (scratch/agent/s6542_run.sh) at dd4 lvl1; dump FB on consecutive VIs immediately before and after a toggle (pose delta ~0), feed a pair into tools/owner_sheet_s6545.py style sheet. Positive control: terrain-fraction differs between the two when forced fully (inf vs cap 0).
Outcome logic: visible extra terrain at inf in the same pose -> recommend inf for dd>1 to owner; none -> cap0. After that: next binding limit past dd4 (dd6, 0x80800000 pool).
