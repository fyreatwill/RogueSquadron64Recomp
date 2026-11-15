# NEXT (s7391)
HYPOTHESIS-ID: fb-cpu-reader-census

s7390 widened build_fbld to LD (ld/ldc1) + do_lwl/do_lwr and added the report classifier (tools/s7389_fbld_report.py: LIVECLASS,
VERDICT, rc 3 = reader candidate). Route rerun: 0 live colour loads on any path, controls LD 5.6e6 / LWLR 1.0e7.

Work unit:
1. Fold s7390_fbld_wide_levels from SOAK-RESULTS (reports scratch/s7390q/report_l*.txt). Pass = alive, VERDICT no-reader, PATH
   kind=ctl path=LD present. On rc 3: the LIVELOAD line names fn + file:line + page + path -> read the function
   (H-real-reader: copy/blit/sample shape -> r2r=0 needs a targeted readback for that buffer; H-reuse: heap/DL code -> add the
   function to klass() HEAP with the evidence in the session entry).
2. On pass, CLOSE fb-cpu-reader-census in CURRENT-TRUTH item 1 and pivot (new HYPOTHESIS-ID): next Next-steps item per
   ITERATION.md -- items 2-10 are owner items, so item 16/17: a new idiom-class audit or the next open 3c rung.
   Do not re-run fb-load watches without a new code path to cover.
