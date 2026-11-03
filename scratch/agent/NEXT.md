# NEXT: ROGUESQ_HANGAR_FOV under the owner's screens (ASPECT 16:9 / 21:9)
HYPOTHESIS-ID: hangar-fov-optin

Context: s6836 landed ROGUESQ_HANGAR_FOV (craft-select cam 0x800CD670 only; fovy replaced before the s6104 aspect /
s6112 vpw patches). Verified at 4:3 only. The owner plays 21:9 and 16:9, where the s6104 aspect scale widens a3 and the
s6112 vpw patch widens the viewport -> the horizontal FOV at 45 is wider still and the fish-eye stronger.
Hypotheses: H-ok (knob composes: fovy 38 under ASPECT, aspect/vpw scaled as before, frame fills the wide window);
H-clash (the aspect patch or vpw bypasses the craft cam, or the G1d FP_XSCALE frustum widening crops ships at 38).
Run (one build, 4 arms sequential, ~60 s each, route scratch/s6836/arms.sh AP):
  ASPECT=21:9 retail / 21:9 + HANGAR_FOV=38 / 16:9 retail / 16:9 + HANGAR_FOV=38 (add the OWNER-OPT-INS widescreen
  companions: ROGUESQ_OSMEM_MB=12 etc.), ROGUESQ_G3F_CAM in all.
Discriminator: G3F log fovy/aspect/vp for 800cd670 in each arm (expect 38 + the same aspect as the retail arm of that
aspect) and a 4x2 frame sheet at matched pan times. H-ok -> note in OWNER-OPT-INS with the per-screen line, send sheet.
H-clash -> name which patch and fix ordering. Then: next ITERATION 3c ladder rung with an open item (owner items pending:
FPS60 feel, G1d/G3c sheets, hangar FOV value).
