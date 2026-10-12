# NEXT: hangar right-edge thread closed (s4643); pick the remaining hangar artifacts or fall back
HYPOTHESIS-ID: hangar-renderer-artifacts

s4643: right-edge band is ~5 of 1280 px (col 511 + bilinear halo); benign. Thread closed.
Remaining hangar artifacts from CURRENT-TRUTH: rim band and blue holo spikes. Next unit: pick ONE (rim band or holo spikes),
list 2-4 hypotheses and the discriminating measurement in this file before building; reuse tools/edge_band_measure.py-style
offline analysis of existing frame captures first (scratch/agent/s4642_viext/*.png) before any new build.
If neither is tractable, M5/M3 items in CURRENT-TRUTH Next steps 2-4 apply; do not start the rename sweep while the engineering-change gate is near 6.
