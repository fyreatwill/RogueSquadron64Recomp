# NEXT: G1d step 37 - HUD edge anchoring at 21:9
HYPOTHESIS-ID: g1d-widescreen
s6144 fixed the terrain left void (apply_s6144_fpx.py). Remaining in flight: HUD (radar top-right at x~690, lock/status at x~315, enemy marker) sit at 4:3 virtual x; want edge-anchored. 
Work unit: find the HUD element x writers (sprite/overlay submit with 320-wide virtual coords), H-offset (single x-shift per HUD group by (fbw-512)/2*side) vs H-per-element table. Discriminator: shift one element (radar) by +160 px in-run; it must move right in the fb dump (positive control), then bundle left/right anchors under ROGUESQ_ASPECT. Recipe: scratch/agent/s6144_run.sh. Then menus/hangar at wide.
