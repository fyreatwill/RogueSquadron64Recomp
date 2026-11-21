# NEXT (s7745)
HYPOTHESIS-ID: g6c-coverage-l10-l12
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, then any owner report, then new SOAK-RESULTS lines.
CURRENT-TRUTH is ~60 KB: if `wc -c` > 60000 this iteration is MAINTENANCE (ITERATION Step 0), so do that instead of the below.

Unit (if not maintenance): add-anchored stand-in dump window so L10/L12 get a real ON/OFF frame pair (s7744: fixed 10/16/25/31 s
windows missed L10's add bursts at 22-24 s and 29-32 s; L12 crops were scene motion).
- src/main/rs64_standins.cpp ~line 793 parses ROGUESQ_STANDINS_DUMP (a:b:n, 'c' prefix = cut-anchored). Add an 'a' prefix:
  `a<min_adds>:<gap>:<n>` opens window 1 at the first second whose [standins-s] added >= min_adds, and window 2 (forced off) <gap> s later.
  The fbdump side reads the window via upstream_compat.cpp (grep STANDINS_DUMP). Rebuild, then run the gate sweep (--jobs 2).
- Rerun scratch/s7744b_standins_cov.sh with DUMP=a500:6:90 on L10 dd4 + L12 dd4. Score with s7624_flicker_score + s7628 sheet.
  Also look at the crops yourself: an ON-only object, not motion.
Outcomes: L10 crops show far objects ON-only -> H-gain proven on a 3rd level (add the rows to the owner sheet); flicker ~ control
even inside an add burst -> stand-ins added but not visible (investigate size/depth: why-k far=35 units?); misplaced object -> H-defect.
