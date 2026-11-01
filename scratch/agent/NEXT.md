# NEXT: G3 render fidelity -- same-camera port vs retail frame pair on the scripted lvl1 briefing fly-over
HYPOTHESIS-ID: g3-briefing-oracle-diff

s6737 closed the G3 border/edge class: the right column (s6736) was the only clear-only border. The earlier in-flight
retail comparisons (s5978/s5998) were eyeball-only, with different cameras. The pre-mission briefing fly-over (cw 640,
640x336 VI, epoch ~6 in [g1d-reach]) is a scripted camera path with no player input, so a frame N VIs after its first
VI should match between the port and retail. That gives a real pixel diff.
Hypotheses: H-match (port == retail within filtering/dither noise: per-tile mean |diff| < ~8 lum everywhere);
H-geom (port-only missing or extra geometry: tiles with diff > 40 clustered on objects/terrain);
H-shade (colour/fog/combiner deltas: diff spread smoothly across the frame, mean offset in one channel).
Steps:
1. Retail: docs/G3-RETAIL-PIXEL-ORACLE.md (angrylion m64p) + scratch/agent/s5978_retail_flight.sh route. Note the VI count
   of the first 640-wide VI after the level-select A press, then dump fb at +60, +120, +240 VIs. Positive control: the
   dumped frame is non-black and 640 wide.
2. Port: the same VI offsets via FB dump on the forced lvl1 route (scratch/s6737/dense.sh recipe, FB_DUMP_MODE / fbd tools;
   key the offset on the first cw=640 epoch after the level select, i.e. the [g1d-reach] epoch 6 start).
3. Diff 640x336 RGB: per 16x16 tile mean |diff|, heat map, and the top-10 tiles cropped side by side. Check the same-run
   control first: two port dumps at the same offset from two runs must agree, or the path is not deterministic and
   the method fails. In that case fall back to the s5978 coarse element-class check and say so.
Expected: H-match closes G3 in-flight at pixel level. H-geom/H-shade name the draws to chase in the next unit.
