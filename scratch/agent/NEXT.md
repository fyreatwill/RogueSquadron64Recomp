# G1d: name the title-phase backdrop photo x-origin and the garbage rect at wide
HYPOTHESIS-ID: g1d-widescreen
s6228: select screen centred at w796/w1024; title phase still shows photo backdrop offset right (starts 36% @w796, 50% @w1024, cropped right) and a bottom-aligned garbage rect ending where the photo begins. Stable across frames and widths.
Hypotheses: H-cam2 (photo drawn through a different camera/viewport whose scale s6227 did not touch, e.g. a 512- or 320-wide cam), H-B (garbage rect is defect B pool overlap, independent of photo offset), H-layout (guest lays photo out from fb width, e.g. fbw-derived x).
Discriminator: one run at w900 with ROGUESQ_LOG_G1D_CMD=1 during title phase: dump per-cmd min-x/max-x/size of every TEXRECT/tri sorted by area; the photo is the largest; read its [vpw] camera line (w, cx) and find whether x = cx-derived (H-cam2) or fb-derived (H-layout). Positive control: s6227's text texrect origin 193 must reproduce in the same run. Arm DROP_EXTRA=0x25000 in the same session for the garbage rect.
Reuse scratch/agent/s6228_run.sh (screenshots) and s6227_run.sh (cmd log parsing).
