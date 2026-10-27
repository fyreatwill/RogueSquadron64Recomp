# NEXT: G3c(a) real haze-coloured edge fade at dd3
HYPOTHESIS-ID: g3c-owner-visual

s6356: AA74 write (ROGUESQ_EDGE_FADE_R2=r0,r1,116,68,R,G,B) proven live and distance-selective. Now make it the actual fix for the jagged far-terrain edge.
1. Sample horizon sky colour from a flight frame (e.g. scratch/agent/m6/g1_lvl1s6355_ctl/fbd/fb_0003423_w512.ppm, near the terrain/sky boundary) -> R,G,B.
2. Write soak scratch/agent/soak_queue/s6357_g3c_skyfade.sh modelled on done/s6355_g3c_r2_redctl.sh: arms nofade (dd3 only), fade (R2=<edge-8>,<edge>,116,68,R,G,B) where edge ~ the dd3 terrain footprint radius (tune: arm a 18..26, arm b 26..34). Same hold/dump flags.
3. Fold: g3c_edge_score per arm; view far-edge frames; build owner contact sheet nofade vs fade at the same phase. Expected: fade arm edge blends into sky (no stair-step); if stair-step persists beyond the fade radius, fade radius is smaller than the drawn footprint -> raise it.
