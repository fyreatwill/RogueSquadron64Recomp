# NEXT (s7463)
HYPOTHESIS-ID: soak-stall-measure-coverage

s7462 (class DR): m6 void attempts now score stalls (fail() -> vilog_stalls.py, summaries void_holds=, verdict counts it;
M6_VOID_BLIND=1 old). Queued scratch/agent/soak_queue/s7462_m6_void_holds_ctl.sh.

Step 1: fold s7462_m6_void_holds_ctl from SOAK-RESULTS.md / its log.
  - CONTROL PASS (P allattempts-failed void_holds>=1, keys "-att1 exitrc=... fs_holds>=1"; C alive_at_end=1 void_holds=0) ->
    close class DR in CURRENT-TRUTH item 1 (one line) and LEAVE this slug: the m6 stall series is done.
  - P void_holds=0 with plant begin in fail_att1.log -> check whether the log has fs= rows during the hold (DIAG_QUIET may
    suppress [vi] rows pre-mission); fix the scorer input, re-queue once.
  - P passed the gate (no void) -> the hold ended before WAITN expired; raise dur, re-queue once.
Step 2 (new slug): next ladder item. Owner items (CURRENT-TRUTH 2-9) await the owner; take an M3 idiom-class audit
  (ITERATION item 3) with a new class, or the G5 renaming sweep (item 4). Do not open another harness-meta class unless a
  fold shows a concrete misread.
