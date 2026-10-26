# Next: G3c(a) jagged far-terrain edge - read the s6304 fog-ramp soak
HYPOTHESIS-ID: g3c-owner-visual
s6304 queued scratch/agent/soak_queue/s6304_g3c_fogramp.sh (dd3_nofog, dd3_fog, retail_fog, forced magenta fog FF00FF). Fold its SOAK-RESULTS line, then:
  python3 -I tools/g3c_fogramp.py scratch/agent/m6/g1_lvl1s6304_<arm>/fbd 0 20   (per arm)
Positive control: fog arms magenta_px_total >> 0, nofog ~0. Outcomes: far third heavily magenta at dd3 -> H-fade refuted, edge is footprint trapezoid (then fade/clip the outermost cell ring or scale footprint softly); far low, mid/near high, retail far high -> H-fade selected, scale ramp end by dd in a fixup script; everything <2% -> fog factor ~0 in flight, probe F5 vertex alpha next.
Also ask owner re ROGUESQ_CULL_SPIKE default (G3c b).
