# NEXT (s7259): fold s7258_dd6_auto_stack, then the dd6 stack image check
HYPOTHESIS-ID: widewin-heavy-window-cost
State (s7258): stack (R48+MERGE0.4/E16) removes dd6r's late dips and cuts the L4 window 14.04 -> 9.82 ms (s7257); it is now auto in the dd6 bundle
(main.cpp [s7258]; ROGUESQ_DD_WIDEWIN_STACK=0 off). Queue: s7258_dd6_auto_stack (SOAK_NEEDS_IDLE=180; arms auto, off, offd).
1. Fold: control offd must be flat 30 in t=77-97. auto must show [s7258] + [s7239] merged>0 and ~9.8 ms / 0 beyond-route dips; off ~14 ms + late dips.
   auto == off -> the auto path is not engaging in mission: debug the reinit (S7239Init/S7246Init latch order).
2. Hypotheses for the open image question at dd6: H-clean (stack removes no visible terrain at dd6, as at dd4) vs H-loss (R=48 skips cells that
   dd6's bigger footprint shows, or merges crack on far ground). Discriminator: the s7247 capture pair at dd6 21:9 L4 (STACK=0 vs auto, same
   fixed camera spots, synthetic-patch positive control), seams px/frame + terrain-removed fraction. H-loss -> narrow the auto to MERGE only or raise R.
3. If the soak did not run: do step 2 offline-scored captures only when the screen is unlocked; else the next G-ladder item (G5 list).
