# NEXT (s7750)
HYPOTHESIS-ID: g6c-coverage-other-levels
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, then any owner report, then new SOAK-RESULTS lines.
s7749 closed L12 coverage: "85/92 never added" was a 120-try window; lifetime 93/131 added, 24 script-owned (never grid-linked),
7 cond, 7 off-screen culled, v_far=0, activation control 27/0.
Unit: fold the queued soak s7749_life_L10_L1 (scratch/s7749b_soak, `s7749 arm=` lines in its soak log). If it has not run yet
(it needs 300 s HID idle), run it in-session: `zsh scratch/agent/soak_queue/s7749_life_L10_L1.sh` (then move it to done/).
Hypotheses / outcomes:
- H-clean: every never-added item is UNLINKED-NEVER, COND or CULL-OFF (as L12) -> G6c coverage closed on 3 levels; take the next
  ladder rung (nothing open: G6 awaits the owner's look; pick the oldest owner item whose closing evidence is single-source).
- H-far: some linked, condition-met item culls by v_far at dd4 -> the stand-in far multiplier misses that level's view (check
  rs64_vt_farmul path for that subtype) - real defect.
- H-novt: culls by v_novt (no view test ran) -> the bucket rejects before the view test (slice group / flags) - read the
  addNpcToVisibilityBucket entry for that instance.
Note L10 u104 read 273/273 never-added at 120 tries in s7748; expect the lifetime table to reverse that as on L12.
