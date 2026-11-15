# NEXT (s7389)
HYPOTHESIS-ID: render-to-rdram-double-pass

s7388 closed the r2r=0 abort-cut stripe on two lines (s7387 window A/B old build; s7388 present-side probe ROGUESQ_S7388_PRES: old path
3/3 presents the stale 0xA40000 upload, fix 0/3, branch-B raw presents all black). Soak s7388_r2r_fix_levels is queued.

Work unit:
1. Fold the s7388_r2r_fix_levels verdict from SOAK-RESULTS (pass = alive, 0 crash, knob line, [s7388-pres-sum] present with upl=0 hot=0
   on L1/L4/L12). If it passes: OWNER-OPT-INS row -> "ready to try" (default stays on = retail; owner decides), close CURRENT-TRUTH item 1
   down to 3 lines, and take the next CURRENT-TRUTH Next-steps item (item 2+) per ITERATION.md priority.
2. If it fails (hot>0 or upl>0 at r2r=0): the probe line names fb/t/nz -> find which path uploaded despite the s7387 skip (hypotheses:
   H-other-upload = a second uploadRAM caller, e.g. a non-screen fb path; H-flag = renderToRAM read differently at that moment
   (extended.renderToRAM toggled); H-probe = branch-B storage with real content not from a stale buffer). Discriminate by the probe's
   branch/upl fields alone before building anything.
Residual-risk check (optional, cheap): grep for game CPU writes into scanned fbs (any title/text drawn by the CPU straight to the fb would
be dropped at r2r=0) - the probe's upl count in the CPUUP arm lists every hash-change fb; all 5-6 per run were garbage, none real content.
