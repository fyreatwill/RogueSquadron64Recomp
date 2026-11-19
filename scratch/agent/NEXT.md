# NEXT (s7651)
HYPOTHESIS-ID: census-attribution-sweep

G6a/G6b/G6c and the G5 looks wait only on the owner (docs/OWNER-OPT-INS.md). If the owner reports, take that first.

s7650 made tools/s7648_mk8_census.py attribution brace-aware (fn_spans / enclosing_braced, --diff) and found 9 sites
whose D label came from the wrong function. The same backward-scan `enclosing` (range(i, -1, -1) to a column-0 regex
match) is in 10 other closed-class census tools: s7365_invalidation_census, s7373_aq_gate_table, s7375_nolock_threads,
s7430_file_growth, s7533_fz_census, s7535_ga_census, s7549_gi_census, s7591_mr_census, s7604_ra_census, s7615_dq_scan.
Work unit (offline, bounded, ONE iteration for all 10):
1. Move fn_spans/_clean/enclosing_braced into tools/census_attr.py (s7648 imports it; its --controls must still pass 3/3).
2. For each of the 10 tools: add a --diff that recomputes each site's function with enclosing_braced and lists changes,
   without changing its verdict logic yet. One python pass prints a table: tool, sites, changed, changed-and-label-
   depends-on-function.
3. Every changed site whose class rested on the function: re-read by hand and reclassify. Add the s7650 attribution
   plant to each tool that has --controls.
Hypotheses: H-cosmetic-all (changes only relabel diag sites) vs H-hidden (a closed class has a misattributed
behaviour site -> fix it with a same-run control and reopen that class's CURRENT-TRUTH line).
Rules: never touch build/saves; one game at a time; SIGKILL only.
