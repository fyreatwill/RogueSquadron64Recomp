# NEXT (s7271): fold s7270_169_cutscenes (WIDEWIN auto stack in cutscenes at 16:9, owner TV)
HYPOTHESIS-ID: widewin-stack-cutscenes
State: s7270 closed 21:9 dd4 as H-clean (control R0 off-map cull fired 3.36-3.78; off->stack max 1.54 < control spread). The 16:9 run is queued as
scratch/agent/soak_queue/s7270_169_cutscenes.sh (tools/s7270_widewin_cut_mov_169.zsh, SOAK_NEEDS_IDLE=120). Read its SOAK-RESULTS line and
scratch/s7270/rank_s169.txt (+ run_s169.log).
Hypotheses: H-clean169 (0->1 edges inside the mid-second control spread AND 1->2/2->0 control edges >= ~3, the green-field shot) -> close the thread,
OWNER-OPT-INS 16:9 note; H-cut169 (an off->stack edge above the control max that a view shows as lost ground/pop) -> gate the stack off in cutscenes;
control does not fire -> VOID, check [s7031] ph2 ocull > 0 and the w1024 gate reached the playlist (frames > 40000).
View: python3 tools/s7270_tog3_sheet.py scratch/s7270/s169.raw out.jpg 8 <frames of top 0->1 and top control edges>; delete the 8.8 GB raw after.
If the soak has not run (owner active), do NOT babysit: take the next ladder item (CURRENT-TRUTH Next steps; all remaining are owner-look, so 3c G-ladder).
