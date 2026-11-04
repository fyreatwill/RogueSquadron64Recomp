# NEXT: measure the 80-row edge array overrun, then decide whether deep rows need real storage
HYPOTHESIS-ID: g1d-span-edge-overrun

Why: s6882 removed the cost of the runaway rows, not the overrun. The reader path is inference (row count never logged), and rows past 80 still write the max array into the span table at 0x80130DB0.
Hypotheses: H-harmless (rows >= 80 are outside the 64-row tables anyway, so no visible terrain depends on them) / H-corrupt (max[i>=80] writes overwrite live span bytes, so far terrain cells are wrong at dd > 1 or wide) / H-other (0x7F7F reaches the bound by some other path; row counts stay under 80).
Measure: one instrument, one build, env-gated: per call at 0x800425F8/0x80042740, log max row count ($s0 + 1), first row, and count of rows with index >= 80, plus a before/after hash of span table bytes the edge writers touch. Run 21:9 dd4, 16:9 dd4, 4:3 dd4, 21:9 dd1 with the s6882 recipe (scratch/s6882/run_c.sh).
Control: a forced arm that writes a known pattern at row 80 must show in the log, or a zero says nothing.
Outcomes: H-harmless -> record and close. H-corrupt -> give the edge arrays real storage or clamp the walkers behind one env; compare frames at same pose with the fixed g3_aspect_crop. H-other -> name the true writer.
Then: FPS60 + 21:9 dd4 and 16:9 dd4 rate after the fix; explain ucode 20-30 ms here vs 5.4 ms in s6810 (recipe logging or store diag?). Run a no-recipe-logging arm.
Small open item: best sx sits 1.00% under sy at both widths; measure the 4:3 picture box (1106 px wide; 512:448 x 960 would be 1097).
If an owner report arrives, it outranks this.
Ask owner when a human is next on: add tools/regen_front.sh, regen_replay.sh and regen_verify.sh to the CLAUDE.md regen order (owner file, not edited). Decide whether to regenerate the live tree; regen trees were compared by object at s6881 only, never linked or run.
Owner judges: docs/owner_sheet_s6882_219_dd4.png, docs/owner_sheet_s6881_wide_dd4.png, docs/owner_sheet_s6880_219_depth.png, docs/owner_sheet_s6879_wide_depth.png, docs/owner_sheet_s6874_dd_edge.png, docs/owner_sheet_s6860_lvl10_hud_ab.png, docs/owner_sheet_s6861_pause_hud_ab.png, docs/owner_sheet_s6872_optin_samepose.png.
Open, not queued (G4): FPS60+dd3 at 300 s, FPS60+dd2 on lvl10, wide bundles at 300 s continuous, 21:9 lvl5/lvl10 at 300 s. Owner can lift the park for these. lvl10 cloud clock only on an owner report.
