# NEXT (s7918)
HYPOTHESIS-ID: ct-maintenance-s7918
CURRENT-TRUTH is now > 60000 B (s7917 added the island B close line) -> Step 0 MAINTENANCE, no experiments:
- Migrate Next-steps item 0 (G3 pre-flight islands, s7891-s7917 detail) and item 12 (G3 det sweep s7832-s7893, ~210 lines) verbatim
  to PROJECT-OVERVIEW "(s7918 maintenance)"; leave one-line CLOSED verdicts + pointers. Keep the s7893 retained-manifest/owner
  launchd prune note (operational). Refresh the headline; renumber the backlog monotonically. Target net shrink >= 15000 B.
- The s7804/s7848 zst lint scopes tools cited in CURRENT-TRUTH AND PROJECT-OVERVIEW: run `python3 tools/s7651_gate_sweep.py` (--jobs 2)
  after the move; 0 new RED required.
After that (s7919): every ladder rung is closed or awaiting the owner (OWNER-REVIEW-QUEUE.md). Check crash_reports, owner answers,
SOAK lines first; then take ITERATION 3c's first non-closed rung (re-check G5c freeze-gap / G1e present cadence on a fresh owner-recipe
soak if nothing else is open).
