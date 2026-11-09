# NEXT: G1c phase 2 — do fully fogged far cells cost frame time for nothing? (fogged-cell cull at dd>4)
HYPOTHESIS-ID: g1c-fogged-cell-cull
Context: s7020/s7021 put the dd>4 limit on per-cell cost (+2048 cells = gfx +1.72 ms/frame, game +0.91). s7007 found the 21:9 dd4 far slab
fully fogged (fog colour (152,107,98)). s7028/s7029 closed bridge micro-trimming (H-call). Cells drawn entirely at fog colour add cost and no image.
G5i/owner items: nothing to run (CURRENT-TRUTH items 1-14); check that first.
Hypotheses: H-fogwaste (a large share of the cells beyond the dd4 radius render at >=99% fog: culling them recovers most of the dd6 cost with no
visible change), H-visible (outer cells still carry non-fog pixels: culling them pops terrain, so the lever is the fog distance, not the cull),
H-gamecost (the cost sits in the game-side stream walk regardless of draw: cull at submit saves rsp only).
Discriminator, one build: per frame, for each cell ring beyond the dd4 radius, the fraction of its RDP pixels at fog colour (reuse the G5b
TRIS dump + framebuffer, scratch/s6894 tools), and a same-run tog3 arm ROGUESQ_DD_FOGCULL=0/1 (skip processGridCellByDistance submit for cells
whose near edge is past the fog end distance) measuring rsp/run ms/frame (tools/g5e_cost_by_parity.py split xor8) plus terrain-fraction and an
owner contact sheet of the same camera dd6 cull off vs on. Positive control: FOGCULL with the fog end forced to dd1 radius must visibly cut terrain.
Recipe: copy scratch/s7029/arm.zsh, L1 dd6 21:9 WIDEWIN cap 10240, OWNER_TIMING=1, 290 s.
