# NEXT: opt-in fix for the eye-cell near-plane clip (retail behaviour, s7109)
HYPOTHESIS-ID: fps60-wall-nearfix
Context: s7109 showed the canyon-wall near clip at retail settings (17.4 eye-cell near-z losses per wall-hug minute vs 15.9 at the
owner recipe). The push-out (applyPlayerVehicleStateUpdate 0x8004CD00) keeps the camera 2*near from the wall using the camera
struct near s2+0x2C = 30; ROGUESQ_DD_NEAR=<m> (tools/apply_s6031_far.py, already built) scales ONLY the guPerspective near arg in
setupCameraMatrices, so DD_NEAR=0.5 puts the plane at 15 with the push margin unchanged.
Unit: two sequential L6 runs on the owner recipe (scratch/s7099/arm.zsh 6 4 <name> "<s7109 instrument env> ROGUESQ_FPS60=1"), arm A
without DD_NEAR (or reuse s7108 as A if the recipe matches) and arm B with ROGUESQ_DD_NEAR=0.5. Better: add a `tog` mode to DD_NEAR
in apply_s6031_far.py (odd absolute mach seconds, like S7108_CAMWIDE) so both arms live in ONE run, then split with
tools/s7108_split.py (its parity clock is the same) incl. the --shift 0.5 control.
Positive controls: the [s7108] line must print pnear=15 in the on state; losscan must still flag >= 300-cell swaps in the off state.
Also measure z-fighting: count frames with terrain/object flicker away from walls (losscan "other" rows per minute per state) since
halving near halves the depth precision near the camera.
Hypotheses:
 H-fix    eye-cell near-z losses drop >= 3x in the on state with "other" losses unchanged -> offer ROGUESQ_NEAR_FIX (or document
          DD_NEAR=0.5) in OWNER-OPT-INS with a before/after sheet; owner decides the default
 H-margin losses unchanged -> the clipped tris are closer than 15 (the push-out lets the camera nearer than 2*near on some swaps);
          read the chase log's push distance on the dropped swaps and fix the push-out instead
 H-zfight losses drop but "other" rises -> try 0.7, or scale near only while the push-out is active
