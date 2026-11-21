# NEXT (s7746)
HYPOTHESIS-ID: g6c-coverage-l10-l12
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, then any owner report, then new SOAK-RESULTS lines.
CURRENT-TRUTH is 59.9 KB. If `wc -c` > 60000 this iteration is MAINTENANCE (ITERATION Step 0); it needs to shrink toward 35 KB anyway.

Unit (if not maintenance): L12 visibility in a later window. s7745: L10 has an ON-only object on screen (H-gain); L12 anchored at
t=9.96 s (a150) read 162 vs forced-off ctl 497, so the stand-ins were added but not visible.
- Rerun scratch/s7745_standins_cov.sh with only the u124 arm, DUMP=a600:6:90 (L12 adds peak ~585-677/s near 50+ s, see
  scratch/s7744b_soak/log_u124.txt), HOLD 150. Same scoring (s7624 flicker + paint control, s7628 sheet). Look at the triplets yourself.
Outcomes: win1 well above ctl with an ON-only object -> H-gain on L12 too (add the L10 n5752 + L12 rows to the owner sheet, ask
the owner); win1 <= ctl again -> L12 stand-ins are not visible: dump why-k/vt reasons (ROGUESQ_STANDINS_LOG [standins-why]) for the
added items and check depth/size (far=35-unit question from s7744).
