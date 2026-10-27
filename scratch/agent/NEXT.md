# NEXT: rerun G3c(a) with per-arm flight-width gates
HYPOTHESIS-ID: g3c-edge-arm-route-gate

Run the same four arms from `scratch/agent/s6394_edge_arms.sh`, but make the
route predicate per-arm: retail and draw-distance=2 must show the phase-5
target-store witness followed by a stable `width=640` VI flight row; aspect
only and combined must show the witness followed by `width=796`. Keep the
positive framebuffer-hash/terrain controls and zero crash/stall checks. Score
only dumps after the arm-specific gate passes.

Competing hypotheses:

- H-edge-fog: dd2 changes edge excess relative to retail at the same width;
  aspect-only does not change it, and combined follows dd2.
- H-edge-grid: dd2 and combined share the same edge signature regardless of
  aspect, indicating the expanded terrain-cell boundary.
- H-edge-aspect: aspect-only changes edge excess relative to retail, and
  combined follows aspect-only rather than dd2.
- H-gate-only: the score ordering collapses or changes once all four arms have
  valid per-arm flight captures.

DISCRIMINATING MEASUREMENT: one concurrent four-arm run, one build, with the
phase-5 writer witness and arm-specific width gate. A complete valid table
selects fog/grid/aspect by score ordering; any arm failing its gate leaves the
visual hypotheses unevaluable and selects only a route-gate correction.

Exact command: `zsh scratch/agent/s6394_edge_arms.sh` after updating its
per-arm gate, then run `python3 tools/g3c_edge_score.py` on each gated `fbd`
directory. Do not change runtime defaults or visual code.
