# NEXT: pixel-qualify ROGUESQ_W_SHEET_POS (s7127 corner-hairline cull) and give the owner a before/after sheet
HYPOTHESIS-ID: wsheet-escape
State (s7127): H-pos CONFIRMED. The s7125 escaper class is a perspective tri with all W > 0 (corner W ~5400, near pair ~3.5e5-6e5),
one vertex clamped to a guard-band corner ((-199,-112), (-398,-224), (994.8,-112) at 16:9, scissor 0,0,795,447) and the other two within
1.6-4.3 px: a ~400-1100 px hairline wedge from the screen corner (a knife line / dark sky band). The mixed-sign W_SHEET rule cannot see it.
Fix landed default-on in lib/rt64/src/gbi/rt64_gbi_rdp.cpp: ROGUESQ_W_SHEET_POS (=0 restores s7126), logs [wsheetpos] + DROPLOG.pos,
same-run log-only control [wsheetposc]. Log evidence: n2 27 fires, all hairlines; offline over k7+r1-r3+n1 the final rule selects only the n1
escaper. Missing: a PIXEL check (logs only so far = single line of evidence for "no new missing geometry").
Competing outcomes of the pixel check:
  H-fixed : frames with [wsheetpos] fires show sky where angrylion shows sky / flat band, no dark hairline; mean|d| on those frames <= neighbours.
  H-harm  : a fire frame loses visible terrain vs angrylion (the wedge also carried real ground pixels) -> tighten (base <= 4 px, or clamp W
            instead of drop) and re-test.
  H-miss  : a dark hairline is still drawn on a frame with no fire -> another class (look at its kept-log line, NLOG T/N included).
Step 1: add ROGUESQ_W_SHEET_POS=t (odd 24 MHz seconds on, same clock as W_CLAMP=tog) so one stream run carries both arms.
Step 2: one L6 owner-recipe stream run, tools/s7126_arm.zsh (EVERY=1), FROM chosen where n2 fired: n2 fire ticks are in
  scratch/s7127/apex_n2_drop.txt.pos (convert to swap via the run's capidx; tools/s7124_capidx.py). If fires are too rare for a 15 s window,
  use the n2 fire mission-time offset. Replay with frame_replay16, score with tools/s7122_fidelity.py, sheet with tools/s7122_sheet.py.
Step 3: owner sheet docs/owner_sheet_s71xx_wsheetpos.png (fire frames: POS off vs on vs angrylion).
Soak results to fold: scratch/s7127/apex_n3* (final rule, run by s7127 itself).
