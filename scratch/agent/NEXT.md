# NEXT (s7809)
HYPOTHESIS-ID: patch-body-diff-class
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. Any crash/stall or owner report outranks the unit. G6c and all G5 items wait on the owner only.
s7808 closed findAndUnlinkSmallestEntry with an offline differential (tools/s7808_find_body_diff.py, sweep row S7808_FIND).
Unit (class closure, iron-rule-3 style): enumerate EVERY live RECOMP_FUNC in RecompiledPatches/patches.c that overrides a game
function (s7806 counted 9 live gcc patch funcs; skip unused_patch_* and helpers with no retail twin). Classify each:
  (a) has a recompiled retail twin with the same contract -> extend the s7808 harness pattern (random guest state, compare r2 +
      touched region vs the retail body; planted mutant must read H-differ), (b) deliberately behaviour-changing patch (document the
      intended delta, test only the unchanged paths), (c) not offline-testable (calls into OS/RSP) -> say why, rely on [patch-live].
Hypotheses: H-equal-all (every (a) body matches retail), H-differ (some gcc body diverges on an untested branch),
H-hollow (state generator misses the branch: require per-branch coverage counters >0 in the verdict, as s7808 does).
Discriminator: one harness run over all (a) functions; any mismatch names the function + trial. Land as one sweep row.
