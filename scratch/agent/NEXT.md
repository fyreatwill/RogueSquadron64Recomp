# NEXT: G1d unwidened-640 perspective squeeze (s6718 lead)
HYPOTHESIS-ID: g1d-640-persp-squeeze

s6718 showed the s6104 guPerspective patch multiplies the aspect by ROGUESQ_ASPECT_SCALE (fbw/512) in EVERY scene,
including video states that stay 640 wide (640x480 menus). The intro had this squeeze and it is fixed now. Any 640x480
scene that draws 3D (title, hangar, craft select?) is then drawn horizontally squeezed by 1.55 (16:9) or 2.0 (21:9).

## Hypotheses
- H-squeeze: some 640x480 scene draws perspective 3D at wide aspect and its objects are narrower than at 4:3.
- H-none: 640x480 scenes are 2D/ortho only, or set their own aspect, so the factor has no visible effect.
- H-intended: the 640x480 scene is shown widened by RT64 (stretched), and the factor compensates for that.
## Discriminator (one build: log the vsu state in effect at each guPerspective call, aspect in/out; one run per arm)
Hangar route at 4:3 retail vs 21:9: object width ratio (craft or hangar door) in window captures, plus the
[g1d-intro]/vsu log showing which state was live. Squeezed (ratio ~1/2 at 21:9) -> extend s6718 (factor 1.0 when the
live state is unwidened, unless that scene's fb is widened). Then the owner judges.
Datum to fold in: thin line in the 16:9 intro (scratch/s6718/a169/w60_*.png).
