# G1d: does the up_167 texrect sample rows >=21 (stale TMEM)?
HYPOTHESIS-ID: g1d-widescreen
s6237: up_167 tile is 64x21 4bpp (lrt=80, maskt=5 -> 32), identical at 4:3 and wide => game span, not RT64-widened. Hypotheses: H-sample-stale (texrect t-range reaches rows 21..31 or bilinear/wrap pulls them in -> visible noise), H-hash-only (draw never samples them; noise is only cache churn and the visible artifact has another cause).
Discriminator: extend s6234 draw-time log to print the texrect's t range for tgt hash; or run one arm hashing/zeroing rows >= (lrt/4+1) for tiles with lrt/4+1 < height and compare the title frame to the unmodified arm in the same run phase (VI-gated). Artifact vanishes -> H-sample-stale.
