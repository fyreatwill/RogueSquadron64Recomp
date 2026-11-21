# NEXT (s7747)
HYPOTHESIS-ID: g6c-coverage-l10-l12
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, then any owner report, then new SOAK-RESULTS lines.
CURRENT-TRUTH is 60.1 KB (> 60000): THIS iteration is MAINTENANCE (ITERATION Step 0). Compact toward 35 KB, no experiments.

Unit after maintenance: why L12 stand-ins are added but invisible (s7746: ground-flicker null at 10 s and at the 62 s add peak,
passing ground paint controls; L10 visible 6.2x). Hypotheses:
- H-clip: L12 items sit beyond the game's far plane (why-k far=30.03 vs PASS dmed~132) and the ucode clips them.
- H-size: on screen but sub-pixel / under the LOD threshold.
- H-drop: on screen and sized, but the submit/DL path drops them (check [standins-dl]/[standins-psn] counts per add).
Discriminator: ONE instrument in src/main/rs64_standins.cpp logging, per added item, eye-space z vs far and the projected screen
bbox (w,h px); run L10 (a500) and L12 (a600) arms in one recipe (scratch/s7745_standins_cov.sh as template) and score with
tools/s7746_ground_flicker.py. Outcome table: z>far only on L12 -> H-clip; bbox <2 px -> H-size; neither -> H-drop.
