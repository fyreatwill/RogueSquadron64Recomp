# NEXT: does the s7037 dd6 auto bundle (off-map fog-depth cull) cut cutscene backgrounds? (G5h-style check of the owner's max recipe)
HYPOTHESIS-ID: dd6-bundle-cutscene-check
Context: s7038 closed G1c phase 2 on flight poses (bundle <=0.23 vs A/A 0.00, sheets docs/owner_sheet_s7038_dd_closeout_l*.jpg). The auto bundle is ON
whenever dd>=6 + WIDEWIN, including cutscenes, which were never checked with it. Cutscene cameras sit off the flight path and look across off-map
terrain (s6908-s6911: cutscene levels author tiny pools; floor 4096). Risk: the cull removes ground the cutscene camera sees (sky voids like s7032 R=2).
Unit: reuse the s6908/s6909 cutscene route (scratch/s6908/arm.zsh; AT THE MOVIES playlist s6909) with arms, one game at a time, same frames:
 dd6off (21:9 dd6 MELT WIDEWIN cap 10240 + ROGUESQ_DD_OFFMAPCULL=-1), dd6b (no OFFMAPCULL env), dd6b2 (A/A), FOGCULL=0.3 positive control.
Score per cutscene frame pair with the s7032 scorer logic (or g3 oracle frame matcher if frames are not phase-locked: phase-gate on VI, rule 2).
Hypotheses: H-clean (dd6b = dd6off at A/A on every cutscene; control fires) -> note in OWNER-OPT-INS; H-cut (some shot loses ground) -> gate the
bundle to flight only (mission state) or raise K for cutscene cameras, re-run same frames; H-unphased (frames not comparable) -> fix phase gate first.
