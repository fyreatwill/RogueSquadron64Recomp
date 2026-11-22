# NEXT (s7804)
HYPOTHESIS-ID: retained-format-lint-gate
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. Any crash/stall or owner report outranks the unit. G6c and all G5 items wait on the owner only.

Unit: make the s7802/s7803 defect class (a tool reading a retained scratch/ capture by raw path/glob after the capture was zstd'd,
silently reading 0 windows / fewer logs) un-reintroducible. Build ONE static gate tools/s7804_zst_blind_lint.py, add it to the
s7651 sweep (ARGS + EXTRA_GATES):
- enumerate every tool the sweep runs (s7651 ARGS keys + EXTRA_GATES + *_census.py) and every tool cited in CURRENT-TRUTH
  (grep `tools/[a-z0-9_]+\.py`);
- flag a tool whose source globs/opens a raw capture extension (sample_*.txt, log_*.txt, run.log, *.cap, *.bin under scratch/)
  without importing rs64_zopen (or an explicit `# zst-ok:` waiver with a reason);
- for each flagged tool, test reality: does the default/ARGS input dir hold the .zst form? (RED only if it does = live blindness;
  WARN if no retained input).
- planted control in the same run: a temp tool with `glob('sample_*.txt')` over a temp dir holding sample_1.txt.zst -> RED; the
  same with zopen -> GREEN. Exit 0 iff 0 RED and both control arms right.
Hypotheses: H-clean (s7802/s7803 fixed every live member -> lint GREEN, class closed with a guard), H-more (a cited/swept tool still
reads raw -> fix it via rs64_zopen in the same iteration), H-noisy (the static pattern flags many non-capture globs, e.g. .o / .c
-> restrict to scratch/ capture paths and say so).
Expected: H-clean or 1-2 H-more members; RESULT pinned in the sweep regex.
