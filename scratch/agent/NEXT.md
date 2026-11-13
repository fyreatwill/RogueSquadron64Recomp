# NEXT (s7270): is the WIDEWIN auto stack (R=88 + merge 0.4 + E16) invisible in cutscenes?
HYPOTHESIS-ID: widewin-stack-cutscenes
Why: s7039 checked only the dd6 off-map cull across AT THE MOVIES; the WIDEWIN stack (s7258/s7266) was qualified in flight only
(s7247/s7259/s7262 holes/seams, s7264-s7268 side edges). Cutscene cameras look across off-map/side terrain that flight never covers,
and the merge pass replaces 2x2 flat far cells with one, which a slow cutscene pan could show as popping.
Design (s7039 template, rule 2: ONE run, same-run toggle): copy scratch/s7039/mov.zsh (AT THE MOVIES route, private wd scratch/s6908/wd,
owner save untouched) -> scratch/s7270/mov.zsh; 21:9 FPS60 dd4 WIDEWIN=1 CULL_SPIKE, with the stack cycling per second via a tog3
on R/MERGE if apply_s7233/s7239 support tog (check `grep -n tog tools/apply_s7233_widewin_r.py tools/apply_s7239_widewin_merge.py`
and main.cpp [s7258]); ph0 = STACK off, ph1 = auto stack (R=88 merge 0.4 E16), ph2 = positive control R=48 (known to eat side cells, s7264).
If no tog exists for R/MERGE, add one in the fixup (same pattern as [s7233] widewin_r tog) - that is the engineering change.
Score: tools/g5h_toggle_rank3.cpp edges 0->1 vs 1->2 vs mid-second control (s7039 thresholds); view top edges; sheet via tools/s7267_tog_sheet.py.
Outcomes: H-clean (0->1 inside control spread, 1->2 R=48 control fires) -> close, OWNER-OPT-INS note; H-cut (0->1 edges with ground
loss/popping viewed) -> gate the stack off in cutscenes (cinematic-mode flag) and re-score; control fails -> instrument VOID, fix first.
Queue as a soak (# SOAK_NEEDS_IDLE=120, drives keys) if the owner is active; do not babysit.
