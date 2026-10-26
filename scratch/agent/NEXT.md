# G1d: wide-title residual 0.05 — skip arms exhausted, switch to logging
HYPOTHESIS-ID: g1d-widescreen
s6252: tri-all arm reads lower=1.0 (confounded, same as "all"); skipping everything is not a usable zero control.
Hypotheses: H-fill-extent, H-tri-rest, H-white-corner.
Next unit: one build logging in ph4 every fill rect (x0,y0,x1,y1,colour) and every tri's screen bbox + draw class, with the fb-lower-band pixel rows (y>=255) that are non-black dumped by x-range; correlate the 0.05 pixel columns with logged primitives. Positive control: a logged primitive known to cover the band must map to non-black pixels.
