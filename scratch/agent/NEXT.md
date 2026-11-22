# NEXT (s7832)
HYPOTHESIS-ID: g3-det-pair-level2
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. Any crash/stall or owner report outranks this unit. G6c and all G5 items wait on the owner only.
Why: lvl1 flight is CLOSED as retail-exact (s7831: two retail refs, retail-vs-retail baseline, pitched positive control). One level is
one sample of G3 in-flight render fidelity (G1(c) "compare a retail oracle frame"). Take a second level with different content (water /
canyon / structures) through the same deterministic pair, so a level-specific render path (combiner, texture, LOD, particles) gets a
retail check.
Recipe: build an EEP with the selected mission set: `python3 tools/g3_eep_patch.py scratch/s6779/r1/lvl1.eep scratch/s7832/lvl.eep
--set 0x31=<m>` (m = 1 first; check the mission is unlocked in that save, else pick the highest unlocked; the copy must re-sign).
Then rerun the s7829 arm-1 pair (see PORTING-STATE s7829 + scratch/s7829/port/run.log for the exact env: g3_menu_pair.sh with
AP0 gate 11.5, PCLOCK=vi, rdplog RENV/XE, OFF=5.75) with EEP=scratch/s7832/lvl.eep. Find the steady flight band with the s7829 tl.py
timeline. One game run at a time (retail oracle + port are the two arms of ONE pair, as before).
Hypotheses:
 - H-exact: world tri dy mode 0, HUD rects exact/path-matched, absent texrects at the retail-vs-retail level (as lvl1).
 - H-pose: a pitched/offset pose again (schedule-dependent, s7829) -> shift the gate and retry once, not a defect.
 - H-residual: a tri/texrect class present in retail but absent or moved in the port beyond the retail-vs-retail baseline -> name the
   PRIM/texture class and write its cause discriminator.
Discriminator: `tools/s7827_tri_yshift_census.py R P --win ... --controls --pose ...` and `tools/s7826_rect_path_offset.py R P --win ...
--none-detail 15`, plus a retail-vs-retail baseline (a second retail run with OFF shifted, `--p-retail` in both tools).
Outcomes: H-exact -> close level 2, take the next level only if it differs in content; H-residual -> its own unit.
