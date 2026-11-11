# NEXT: why the eye gets within 15 units of the canyon wall despite the push-out (s7110 H-margin)
HYPOTHESIS-ID: fps60-wall-margin
Context: s7110 (ROGUESQ_DD_NEAR=0.5 with the new ROGUESQ_DD_NEAR_TOG=1) left eye-cell near-z losses unchanged (8 near30 / 12 near15),
and on-state reference swaps already show the eye cell at the 15 plane. The push-out (applyPlayerVehicleStateUpdate 0x8004CD00)
pushes the 4 near corners (x=w*0.5*240/h, y=120, z=120/tan((fovy+2)/2), times 2*near) out of terrain; s7102/s7103 logged its corners
(CHASE file, pc/rx lines) and re-pushing at exit did not help.
Unit: ONE instrument, ONE run (L6 dd4 16:9 FPS60, scratch/s7110/arm.zsh, same env as s7110 minus DD_NEAR): per presented camera,
log (a) the pushed camera position at push-out exit, (b) the eye position + forward vector setupCameraMatrices passes to the
lookat/view build (same cam struct, s2+8), (c) the terrain height under the eye and the eye's nearest wall distance along forward
(re-use the push-out's own collision call if callable, else the cell triangle plane from S7104/S7105), all mach-stamped.
Then on every losscan eye-cell near-z loss: is |b - a| > 0 (eye moved after the push), or a == b with forward wall distance < near
(push-out probes miss the wall: corner rays vs the centre ray, or the wall is in a terrain cell the probe does not test)?
Hypotheses:
 H-postmove  render eye differs from the pushed position on dropped swaps (chase lerp / shake / later camera update) -> push the
             final eye, or apply the push after that update
 H-probe     eye == pushed position but forward distance to the wall < 30: the corner probes miss this wall -> add a centre/forward
             probe in an opt-in fix (ROGUESQ_NEAR_FIX), before/after sheet
 H-cell      the wall triangles belong to a cell the collision query does not return (cell boundary) -> fix the query cell range
Positive control: the loss list must still flag >= 300-cell eye swaps; (a)==(b) must hold on ordinary non-hug frames.
