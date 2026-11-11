# NEXT: exact-geometry near-plane test where drawn == collision (s7114 run c on-seconds)
HYPOTHESIS-ID: fps60-wall-gap
Context: s7114 proved the eye-cell TriGen and the y-clamp sampler read the identical 25 bytes; with ROGUESQ_S7114_NEARLOD=16 on
(odd mach seconds of scratch/s7114 run c) every near cell is lod 0 plain, so the drawn eye-cell surface IS the collision surface
(exact, 0.000), yet eye-cell near-z losses persist (22 on / 21 off). s7113's clip-space rebuild is biased (do NOT use its world
rebuild or its H-gap row). Build the world geometry exactly instead:
 - surface: hx b= bytes, tile origin x0 = o.x - (qx + fx) * 0.5, z0 = o.z - (qz + fz) * 0.5 (o from the same tick's rx line), node
   y = s8 * sc / 256 + y0, 00-11 diagonal (tools/s7114_hsrc.py coll()). Positive control: the surface at o must equal hx h exactly.
 - camera: eye = bv rd; near-plane rectangle and probe rays from the game's own pu corners (c - p0 offsets, forward 0.140) and the
   s7108 guPerspective near/fovy/aspect args; push-out rays = pre -> c segments of the pu lines.
Hypotheses:
 H-gap     the exact surface pierces the near rectangle (or the near frustum slab) while all 3-4 corner probe segments miss it
           (a ridge or bump between rays): predicts pierce-without-ray-hit on most on-second loss swaps, rare elsewhere.
 H-frame   the near rectangle the renderer clips with is not the one the push-out protects (render basis / near distance / eye differ
           from the pu corner frame): predicts the exact surface does NOT reach the push-out rectangle on loss swaps, yet the eye-cell
           tris are near-clipped; check render near z (s7110: near 15 in clip units) against 0.117 world.
 H-tile    the near-clipped tris belong to the eye cell but the part crossing near lies in a neighbouring tile the probes test with
           another tile's bytes: predicts crossings at cell edges; needs neighbour bytes (add to hx if so).
Discriminator: per flight swap (run c on-seconds; run a for all-lod comparison): pierce(rect) yes/no, any probe segment hit yes/no,
min distance from eye to the exact surface vs f20 and near, on loss swaps vs +-3 s shifted swaps. Offline only, data in scratch/s7114
(push_c.txt, tris_c.bin, losscan_c.txt; tri_c.bin holds the clip-space tris if a cross-check is needed).
If H-gap: fix direction = extra probe rays (edge midpoints + centre) in applyPlayerVehicleStateUpdate, opt-in, qualified by
tools/s7114_parity.py episodes on a tog arm.
