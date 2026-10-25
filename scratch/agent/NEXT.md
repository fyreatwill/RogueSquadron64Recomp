# G1d: verify the s6227 menu-camera fix across widths; re-test defect B
HYPOTHESIS-ID: g1d-widescreen
s6227 fixed the title/select x origin (640-wide menu cams now scale W/640). Remaining: fix_01 title frame showed a garbage block left of the art and off-centre art.
Hypotheses: H-B (defect B corrupt central rect still present, pool overlap), H-phase (fix_01 is a transitional frame, not phase 4), H-window (screencapture window aspect distorts).
Discriminator: run w796, w900, w1024 with the fix, ROGUESQ_LOG_G1D_CMD=1, screenshots every 3 s from 15 s to 60 s; check min-x == (W-512)/2 per width (positive control: w900 gives 193) and read the title-phase frames; if garbage persists, it is defect B: check DROP_EXTRA=0x25000 arm in the same run.
