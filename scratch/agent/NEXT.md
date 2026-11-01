# NEXT: G1d residual -- mission-start transition dark frame with outline box at 16:9/21:9
HYPOTHESIS-ID: g1d-menu-sweep

s6731 finished the menu sweep (owner sheet scratch/s6731/sheet_menus_owner.png) and fixed the pause-logo shard.
Open: one window capture per wide arm at the hangar->mission transition is black with a thin light outline box
(l169 w242 16:9, l219 w256 21:9). 4:3 unknown (2 s sampling).
Hypotheses: H-transition (retail fade frame, also at 4:3: benign), H-crop (s6724/s6726 pillar crop or latched epoch
draws a box outline in the pillar), H-region (s6158 shift / s6156 anchor active on the first swaps of the mission epoch,
radar stamped before the fade ends).
Command: zsh scratch/s6731/menus.sh <tag> <none|16:9|21:9> "ROGUESQ_LIVES_CAP=1 ROGUESQ_FB_DUMP_EPOCH=<e> ROGUESQ_FB_DUMP_VI=1"
(find the mission-start epoch number from the [g1d] epoch lines in scratch/agent/m6/g1_lvl1s6731_l219/run.log near
the second launch; dumps in scratch/agent/m6/<tag>/fbd). Discriminator: box in the 4:3 dumps -> H-transition; box only
wide and inside/at the pillar edge -> H-crop; box coincides with a [region-gate] radar=1 swap -> H-region.
Then G3 render fidelity (hangar artifacts list in CURRENT-TRUTH).
