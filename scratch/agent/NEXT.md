# Next: G3c(a) vertex-level distance ramp (L-fade at vertex shade) vs bare footprint edge
HYPOTHESIS-ID: g3c-owner-visual

s6296: radius has no fog/haze consumer (static). Remaining hypotheses for the jagged far edge:
 H-ramp: retail hides the edge with a distance-baked vertex shade/alpha ramp which dd/aspect cells lack.
 H-bare: retail edge is equally bare (edge excess 0.0212 in s6293) and the opt-ins merely show more of it.
Discriminator, one phase-gated flight run per arm (one at a time): log vertex alpha/shade of terrain
verts vs cell distance (outer 12.5% vs inner) in retail and dd3+aspect, with a positive control
(force-mark all verts). Ramp present in retail only on outer cells -> H-ramp (extend ramp with r);
flat in both -> H-bare (owner question: fade outer ring, opt-in). No mitigation before the writer is named.
Then G3c(b) spikes reference check.
