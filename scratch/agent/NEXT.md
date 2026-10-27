# NEXT: G3c(a) terrain-edge writer audit
HYPOTHESIS-ID: g3c-owner-visual

Closed this far: (b) spikes -> owner decision on CULL_SPIKE (s6351); (c) shake -> H-retail/30fps judder (s6302); red-VTX thread (s6350).
Remaining: (a) jagged far-terrain edge. Continue s6313: find the later colour store/copy in buildGridCellMesh 0x8004BCA0..0x8004BFF4 (RGB x0.2 hook at 0x8004B644 did not darken terrain), name the writer, then scale haze/fade of outer cell ring. Hypotheses: H-fog-unscaled (fog start/end not scaled with dd/aspect), H-cell-boundary (grid footprint edge exposed), H-retail (retail also shows). Discriminator: a colour hook at the real Vtx colour writer with positive control (terrain visibly darkens).
Do NOT run another spike-replay without an independent hardware reference.
