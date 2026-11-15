# NEXT (s7390)
HYPOTHESIS-ID: fb-cpu-reader-census

s7389 closed RENDER_TO_RAM=0 (soak 3/3, owner row "ready to try") and measured its residual risk: 0 guest loads from a live colour
image over the s7386 route (build_fbld, ROGUESQ_S7389_FBLD=1, control 2.8e8). Soak s7389_fbld_levels is queued (L5/L10/L15).

Work unit:
1. Fold s7389_fbld_levels from SOAK-RESULTS (reports in scratch/s7389q/report_l*.txt). Pass = alive, CONTROL PASS, no
   "TOTAL kind=color live=1 LOAD". If a live colour LOAD appears: the row names function + file:line + page -> read the function
   (H-real-reader: copy/blit/sample shape, then r2r=0 needs a targeted readback; H-reuse: heap/DL code on a page still within 8 VIs of a
   SetColorImage = span over-estimate, tighten to the real scissor height). Z live loads on pages >= 0x100000 that are not boot DL
   memory: same split.
2. If it passes, CURRENT-TRUTH item 1 stays closed; take the next Next-steps item per ITERATION.md (items 2-10 are owner items ->
   item 16/17: a new idiom-class audit; candidate: guest-side LD/LWL/LWR + RSP DMA reads of fb pages, the two paths build_fbld does not see).
