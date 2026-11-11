# NEXT: G3 level select + mission briefing at 21:9 (CURRENT-TRUTH item 32)
HYPOTHESIS-ID: g3-fidelity-menus-219
State (s7143): hangar text == angrylion once the scoring rect gets a sub-pixel registration fit (tools/s7143_affine.py); hangar CLOSED.
Run: tools/s7142_arm.zsh with the autopilot extended past the hangar (64:a then 70:start,76:start) so level select and the briefing are
captured, FROM at the level-select entry (check the g5g/time map in scratch/s7142/H1.g5g.txt for swap numbers first). Owner recipe FPS60 dd4
ROGUESQ_ASPECT=21:9, owner save read-only (NO_SAVE_WRITE, no SAVE_FROM). Post: tools/s7141_post.zsh, then s7143_affine.py fit on a non-text box.
Hypotheses: H-equal (all boxes reach the 3D floor under one fit); H-rect (some menu draws still use another RT64 rect path, e.g. fill rects or
copy-mode texrects with horizontalMisalignment, so text stays off after fit: fit text and background separately, a >1/4 px disagreement selects it);
H-wide-menu (menus render 4:3 and get stretched: the x-scale sweep in s7143_textbox.py picks a scale != 1).
Positive control: painted-square PASS per replay; H3-style negative control = the same session's ROGUESQ_RECT_ASPECT=0 arm on one menu.
Side lead: 4:3 hangar VI fbSize (is retail 512x336?) for the 21:9 whole-picture squash claim in s7142.
CURRENT-TRUTH ~59.6 KB: keep edits net-zero (Step 0 triggers at 60000).
