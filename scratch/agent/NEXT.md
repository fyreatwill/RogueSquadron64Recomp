# NEXT (s7807)
HYPOTHESIS-ID: owner-wait-default
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines (fold s7806_gccpatch_L1: pass = alive, 0 fatal, vi_stalls30s=0). Any crash/stall or owner report outranks the unit.
G6c and all G5 items wait on the owner only.

Closed: retained-format class (s7804/s7805), public-build drift (s7806: clean fork build == live tree byte-for-byte incl. patches/).
Unit: take the next CURRENT-TRUTH Next-steps item that is not owner-gated; if none, the first open ladder rung (item 3c).
Candidate if nothing else: exercise findAndUnlinkSmallestEntry (gcc build) at runtime: s6280 recipe (lvl1 dd3, tag
g1_lvl1s6280_dd3_norm) must print `[patch-live] findAndUnlinkSmallestEntry calls=` with nulls=0 bad=0; ROGUESQ_FIND_CTL is its control.
Before running, write 2-4 hypotheses and the discriminating measurement here.
