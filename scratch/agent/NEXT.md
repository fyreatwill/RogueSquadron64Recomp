# NEXT (s7808)
HYPOTHESIS-ID: owner-wait-default
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. Any crash/stall or owner report outranks the unit. G6c and all G5 items wait on the owner only.
s7807: findAndUnlinkSmallestEntry 0 calls at lvl1 dd3 (uncontrolled; FIND_CTL needs a call to fire). Do NOT rerun that recipe.
Unit: take the next CURRENT-TRUTH Next-steps item that is not owner-gated; if none, the first open ladder rung (item 3c).
Optional low-priority: a forcing control for the evictor (find the cache-empty path at 0x801163B0 and make it reachable, e.g. a
ROGUESQ knob that skips cache pushes) so FIND_CTL can fire; only worth it if a patches/ change needs runtime qualification.
Before running, write 2-4 hypotheses and the discriminating measurement here.
