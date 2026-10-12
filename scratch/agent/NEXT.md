# NEXT: how wide is the hangar right-edge garbage band really? (col 511 explains <=1 px)
HYPOTHESIS-ID: hangar-renderer-artifacts

s4642: VI shows 511.9 src cols; col 511 contributes <=1 of 640 output px.
Hypotheses: H-band-1px (band is the col-511 sliver; close thread as benign), H-band-wide (band >1 px: separate cause), H-other-buffer.
Discriminator: measure column-wise garbage extent at the right edge in hangar frame PNGs (scratch/agent/s4642_viext/) for frames at 0x656400 vs 0x6AB400. Control: variance of a known-good column vs edge columns.
