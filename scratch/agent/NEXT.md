# OWNER OVERRIDE 2026-11-04: do ITERATION.md G5 in order. G5a-G5h all fixed or done, owner confirmation pending.
# NOTE: CURRENT-TRUTH is ~59 KB; if Step 0 prints >60000 do the maintenance iteration first.

# NEXT: G1e — the 'none>p99' late presents (73-78 per 5.5 min loaded arm, unchanged by GUEST_QOS): H-margin vs H-present. OFFLINE first.
HYPOTHESIS-ID: g1e-late-margin
State (s6983): GUEST_QOS=1 removes the H-sched lates (15-18 -> 3-4) but those were small; the bulk has no leg over its normal p99.
Late vs normal p50 (B2): rsp 10.43 vs 9.59, run 3.84 vs 2.12, wq 4.37 vs 0.47, kw 3.96 vs 13.02.
Hypotheses:
- H-margin: target 10 + rsp ~9.6 leaves <1 ms slack; any sum of sub-p99 stretches (rsp +0.8, wq +4) crosses the vsync. Predicts the
  late probability rises smoothly with (ph + rsp + wq) and a fitted threshold near the slack separates late/normal (AUC > 0.9).
- H-present: the RT64 present/acquire side is late (drawable acquire, VI-ack block) with the gfx task on time. Predicts
  (ph+rsp+wq) of lates within the normal distribution and the delay sits after send_dl return (ring acq/present fields).
Discriminator (offline, existing captures scratch/s6983q + s6982q, no build): add to tools/g1e_late_leg.py a --sum mode printing per
present s = ph+rsp+wq (and +run), AUC late vs normal, best threshold, and for lates below that threshold the ring present-side legs.
Outcome: AUC > 0.9 with threshold near 16.7 - target -> H-margin: then test ROGUESQ_VI_LOCK_TARGET_MS=8/9 under the same burst
(scratch/s6983/drive.sh with the target edited, ABBA vs 10). AUC ~0.5 -> H-present: instrument acquire/present wall per present.
