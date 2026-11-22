# NEXT (s7805)
HYPOTHESIS-ID: retained-format-lint-gate-followup
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. Any crash/stall or owner report outranks the unit. G6c and all G5 items wait on the owner only.

Unit: the s7804 lint covers only tools whose capture path is a literal. Extend the same idea to argv-borne paths: for every
command line cited in CURRENT-TRUTH and docs/OWNER-OPT-INS.md / OWNER-REVIEW-QUEUE.md of the form `python3 tools/X.py ... scratch/...`,
check each scratch/ argument resolves (raw or .zst); if it resolves only as .zst, run the cited command once and RED on a
traceback / FileNotFoundError (the s7616 failure mode). Planted control: a temp doc line citing a tool with a zst-only arg whose
tool opens raw -> RED; same with zopen -> GREEN.
Hypotheses: H-clean (no other cited command dies on zst-only args), H-more (1+ cited commands crash -> fix via rs64_zopen),
H-unrunnable (cited commands need a game run; restrict to offline ones and say so).
Expected: H-clean or 1-2 H-more; add as a sweep row if cheap (<60 s), else REPORT.
