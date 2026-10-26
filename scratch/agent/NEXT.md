# G1d: wide-title lower-band residual — no attributed draw class
HYPOTHESIS-ID: g1d-widescreen
s6253: ph4 has 0 fills; s6251 attribution refuted; cross-run spread (0.05-0.17) too large to use skip arms.
Hypotheses: H-tri-rest, H-texrect-rest, H-vi-readout (residual is VI/writeback of stale RDRAM, not a draw).
Next unit: ONE run, in-run toggle: skip texrect-all on odd VI frames in ph4 and dump fb at paired frames (even/odd); compare lower band within run. Also dump lower-band non-black x-histogram for the none arm vs bboxR/bboxT x-extents. Positive control: texrect-skip frames must differ from non-skip frames in the glyph rows.
Consider whether this 0.05 residual matters to the owner at all; if the title renders right at 21:9, close it and move to G1e.
