# NEXT: rerun the G3c(a) edge table with a valid wide-flight gate
HYPOTHESIS-ID: g3c-edge-arm-route-gate

Build one run recipe containing the four arms from s6391: retail, draw-distance
2, aspect-only, and combined. Replace the fixed-origin mission gate with a
phase/flight gate requiring the phase-5 DMA witness, stable wide VI width, and
the positive framebuffer controls; record each arm's ordered width/origin
transitions and then compute edge scores only for arms that pass it.

Competing hypotheses:

- H-edge-fog: retail and opt-in edge scores remain comparable after the route
  gate is corrected; scaling haze/fog is the next discriminator.
- H-edge-grid: the scores track the expanded terrain-cell boundary, so the
  outer grid ring is the cause.
- H-edge-aspect: only the widened frustum changes the edge score, implicating
  aspect exposure rather than draw-distance or fog.
- H-gate-only: the prior score differences were dominated by invalid route
  gating and disappear or become stable after accepting allocator-dependent
  origins.

DISCRIMINATING MEASUREMENT: one concurrent four-arm run with the same fixed
camera/framebuffer scorer, but an explicit per-arm pass/fail route table. If
all four arms pass and the score ordering is stable, it selects among the
visual hypotheses; if only the previously rejected aspect arm gains valid
flight evidence or the scores collapse, it selects H-gate-only. Each arm must
fire its positive controls in the same run.

Use the existing s6391 arm recipe/harness, update only its route predicate to
accept the observed allocator-dependent wide origins, then run the Debug target
and the four arms concurrently. Do not change runtime defaults or the visual
edge code in this unit.
