# NEXT: the W_SHEET escape sheet at the owner recipe: a guard-band sky sheet RT64 draws as a dark band (cull did not drop it)
HYPOTHESIS-ID: wsheet-escape
Why: s7125 closed owner-recipe texture fidelity (H-equal), but in w6's cull-ON seconds (L6 dd4 16:9 FPS60, swaps 7635-7641, ~0.2 s)
one thin sheet from a cliff edge across the sky was NOT dropped by ROGUESQ_W_SHEET_PX (no DROPLOG line). Angrylion paints it beige,
RT64 dark. Sheet: docs/owner_sheet_s7125_wsheet_escape.png row 1. A dark streak across the sky is the owner's G5f "knife line" class.
Hypotheses:
  H-span : mixed-sign W, but screen span <= 200 px in RT64's coordinates (the band is long but its triangles are a fan of short ones):
           lowering W_SHEET_PX or using the clamped-W footprint area drops it.
  H-pos  : all three W > 0 (no clamp path); the dark colour comes from a near-zero W giving a huge 1/W shade/tex step: needs a
           separate rule (e.g. W ratio max/min > K over a guard-band span).
  H-other: not the W path at all (e.g. a fill/rect or a different combiner): name the command.
Discriminator, one run: tools/s7125_arm.zsh L6 with ROGUESQ_W_SHEET_STATS=1 plus a NEW kept-tri log in rt64_gbi_rdp.cpp
(ROGUESQ_W_KEEPLOG=<path>: for every texturePerspective tri with min(W)/max(W) < 1/64 OR any W<=0 that is NOT dropped, log tick,
3 screen vertices, 3 W, span) — lib/rt64 edit, so run ./submodule-patches/export.sh and commit. Arm EVERY=1 FROM=7500 as in s7125
so the frame can be replayed and matched (score with tools/s7122_fidelity.py, rect 0,9,369,216). Match the escape frames to keep-log
ticks by mach time (lag ~10-15 ms). Positive control: DROPLOG lines must appear on the known cull frames in the same run.
Outcomes: H-span -> tune the drop rule with a same-run W_SHEET_ALT arm and re-score (no new missing terrain); H-pos -> add the ratio
rule behind an env, default on only after a same-run qualification; H-other -> name the command and its producer.
