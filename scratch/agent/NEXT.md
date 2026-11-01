# NEXT: G1d 21:9 mission-intro pillarbox (s6717 datum; G1f closed, G3d closed s6697)
HYPOTHESIS-ID: g1d-intro-pillarbox

At ROGUESQ_ASPECT=21:9 (OSMEM_MB=12) the lvl1 mission-intro flyover (VI 640-wide mode, origin 0xA4B100,
t~60-70 s of `scratch/s6717/go.sh`) is drawn ~1.9:1 centred, 227 px black bars/side of 2720, ragged right edge
(scratch/s6717/a219/w60_89558.png). Flight (1024 mode) fills. 16:9 intro fills (s6688 run3 w60).

## Hypotheses
- H-fbw-cap: the intro renders into a colour image narrower than 1024 (e.g. 796/854 cap or a separate 640 buffer
  widened by FP_XSCALE only partially), and RT64 pillarboxes the VI 640 mode at the 21:9 target.
- H-scissor: the colour image is 1024 wide but the intro path's viewport/scissor stays at a 16:9-ish width
  (ragged edge = scissor vs geometry mismatch).
- H-vi: game draws full width but the VI mode for the intro (width 640, xScale) makes RT64 crop to a sub-region.
## Discriminator (one build if needed, one run)
Same recipe, 21:9, with an fbd dump at the intro phase (origin 0xA4B100) plus the logged SetColorImage width,
G_SETSCISSOR and viewport for that phase vs flight (grep run.log `[g1d]`/setcimg lines first; the s6717 log may
already carry them). fb content width < 1024 -> H-fbw-cap; fb 1024 but drawn region narrower -> H-scissor; fb full
but window cropped -> H-vi. Fix in the matching layer, re-capture with tools/g1f_bar_score.py (intro bars -> 0-1).
