# NEXT: G1d wide-aspect title-screen garble (s6719 datum)
HYPOTHESIS-ID: g1d-title-garble

s6717/s6718 forced-route runs (autopilot presses Start from t=10) show the title screen (the Luke / X-wing still
behind the STAR WARS ROGUE SQUADRON logo) garbled at EVERY wide aspect and clean at 4:3:
scratch/s6718/a219/w20_*.png (21:9: left ~half black with an orange smeared strip and a white vertical bar; right half
the still zoomed ~2x), scratch/s6718/a169/w20_* and s6717/a219/w20_* (same), scratch/s6718/off219 (ROGUESQ_G1D_INTRO=0,
same), s6717/a43 w20 and dflt w20 (4:3, clean). The owner sees this on every boot at 16:9/21:9.

## Hypotheses
- H-stride: the still is CPU/DMA-written into a 640-wide image while the presenting VI/RT64 path uses another width
  (FB_WIDTH 1024 or the s6718 intro 768), so rows shear / the left part reads stale memory.
- H-texrect-shift: a host-side x shift (HUD anchor s6155/s6156, region shift s6159/s6695, spike-scan guard) moves the
  still's texrect tiles right of a pivot (the image starts at ~x=1360/2720 of the window = a fixed offset).
- H-vpw: the s6112 camera viewport widening (0.8*kv for 640 cams) scales the 2D tiles about the centre (2x zoom on the
  right half fits a viewport scale applied to texrects).
## Discriminator (one build, boot-only runs, no flight needed)
scratch/s6719/dense.sh with the forced-route autopilot schedule (or ROGUESQ_AUTOPILOT=10:start) so the title appears;
arms in ONE batch, sequential: 21:9 default; ROGUESQ_HUD_ANCHOR_AUTO=0; ROGUESQ_VPW_SCALE=1; ROGUESQ_G1D_640PERSP=0;
ROGUESQ_WINDOW_FIT=0. Log the title's video state ([fbw] pfm/vsu + osViSetMode width at the title) and the
SET_COLOR_IMAGE widths during it. The arm whose title is clean names the lever; then fix its state rule like s6718/s6719
and show the owner before/after at 16:9 and 21:9.
Also open (single-source, s6719): WHY a wider terrain footprint x-extent changes the LucasArts logo shape (the cell
set should only add off-screen cells). Read buildVisibleTerrainGridAroundCamera's other uses of the corner vector at
0x40($sp) if the title work leaves time.
