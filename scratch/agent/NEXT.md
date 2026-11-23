# NEXT (s7842)
HYPOTHESIS-ID: g3-retail-flight-det-sweep
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. Crash/owner report outranks this.
Why: s7841 lvl5 render exact; the oracle core now flushes denormals (FPCR.FZ follows FCR31.FS, banner `[core] s7841 ... on` must
appear in every retail run). One lvl5 state fork left: 1-ulp camera y (words 431/446) at port p1 row 341 / retail r2 row 345 (last
fully exact row 254), not FTZ. Name its carrier offline FIRST (no runs needed): rows 255-340 differ only in alloc words 133/146
(0x80137FC4 ptr, 0x80137FF8 index; values vary port run to run). 
Hypotheses:
  H-alloc: the different object behind 0x80137FC4 (heap ptr / index differ) feeds the camera (read its fields: the ramdump only spans
           0x80137DB0..0x801384E0; a port run with a second dump range around 0x8035E600..0x8035FC00 + retail XO with a 2nd --pc-ram-dump
           if the oracle supports several, else one range) -> the 1-ulp comes from different object data.
  H-fpu: a genuine FP op difference (rounding mode window: the game sets fcr31=00000001 = round-toward-zero, FS=0, twice; the port's
         set_cop1_cs rounding handling vs mupen fesetround) -> the row-341 word differs with identical inputs.
  H-sampling: the dedupe sampling hides a dt step difference (check the S7835 dt log around port row 341 vs retail VI trace).
Unit: offline first: scratch/s7841/pose1.py prints the row; add the s7835 dt rows near n=1091 (port) and the camlog rows. If
H-fpu/H-sampling cannot be split offline, run ONE port + ONE retail with the extra dump range. Then move on to 0x31=5 (save
`python3 tools/g3_eep_patch.py scratch/s7832/lvl.eep scratch/s7842/lvl.eep --set 0x31=5`, recipes in PORTING-STATE s7841).
Scorers: scratch/s7829/tl.py flight bands, tools/s7827_tri_yshift_census.py --controls, tools/s7836_hud_elem_census.py,
scratch/s7841/score2.py (ramdump 2x2 pattern).
