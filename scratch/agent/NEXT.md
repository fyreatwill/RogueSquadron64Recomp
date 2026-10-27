# NEXT: G3c(a) phase-gated terrain-edge measurement
HYPOTHESIS-ID: g3c-edge-fade-phase-c6388

The cxd4 reference block is resolved. The next unit is one instrument/build
and one fixed-camera mission run, with retail settings as the control and the
draw-distance/aspect arm that exposes the jagged far-terrain edge.

Competing hypotheses:

- H-edge-fog: the edge is exposed because haze/fog start/end was not scaled
  with draw distance; scaling distance haze removes it.
- H-edge-grid: the boundary is the terrain cell footprint itself; fog scaling
  does not remove it, while an outer-ring fade does.
- H-edge-aspect: the edge is exposed only by the widened frustum; retail and
  draw-distance-only do not show it, but the aspect arm does.

DISCRIMINATING MEASUREMENT: phase-gated fixed-camera framebuffer captures and
the distant-terrain edge pixel fraction for retail, draw-distance-only,
aspect-only, and combined arms. Positive control is a captured frame with the
reported blocky edge in the combined arm. A fog-distance response selects
H-edge-fog; no response plus outer-ring response selects H-edge-grid; an
aspect-only response selects H-edge-aspect. Keep defaults unchanged and retain
owner-viewable before/after frames.
