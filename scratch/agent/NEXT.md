# NEXT: G3 owner-recipe fidelity on L1 and L4 (CURRENT-TRUTH item 28)
HYPOTHESIS-ID: g3-owner-recipe-levels
State (s7130): wsheet-escape CLOSED (both arms pixel-checked, owner sheet docs/owner_sheet_s7129_wsheet_cull.png). Items 1-12 are owner-gated.
L6 at the owner recipe (FPS60 dd4 16:9) matched angrylion to the retail floor (s7125: frac>40 median 0.010, mean|d| 1.85). Other levels unmeasured.
Hypotheses: H-equal (L1/L4 also at floor), H-level (a level-specific diff: terrain/water/texture path L6 lacks), H-dd (extended cells only differ).
Discriminator: per-frame frac>40 and mean|d| per level, and for frames over floor, whether the diff region lies inside the dd1 radius or in extended cells.
Commands: zsh tools/s7125_arm.zsh 1 L1 "" ; zsh tools/s7125_arm.zsh 4 L4 ""  (one game at a time; check screen unlocked first), replay and score as in
  the s7125 PORTING-STATE entry (capture rect 0,9,369,216; tools/s7122_fidelity.py). Owner sheet of the worst frames per level.
CURRENT-TRUTH is 58.8 KB: keep edits net-zero. Owner save rule applies (runner exports ROGUESQ_NO_SAVE_WRITE; never touch build/saves).
