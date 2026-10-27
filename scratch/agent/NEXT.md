# NEXT: remove the stale title gate and rerun G3c(a)
HYPOTHESIS-ID: g3c-edge-arm-route-gate

Update `scratch/agent/s6394_edge_arms.sh` so `TITLE_ANY` is not a blocking
predicate. Run the same four arms using phase-5 plus the per-arm flight width:
retail/dd2 `width=640`, aspect/combined `width=796`. Keep title/armed rows as
informational evidence, and retain positive framebuffer-hash/terrain controls
and zero crash/stall checks. Score only dumps after the arm-specific gate.

Competing hypotheses:

- H-edge-fog: dd2 changes edge excess relative to retail at the same width;
  aspect-only does not change it, and combined follows dd2.
- H-edge-grid: dd2 and combined share the same edge signature regardless of
  aspect, indicating the expanded terrain-cell boundary.
- H-edge-aspect: aspect-only changes edge excess relative to retail, and
  combined follows aspect-only rather than dd2.
- H-gate-only: the score ordering collapses or changes once all four arms have
  valid per-arm flight captures.

DISCRIMINATING MEASUREMENT: one concurrent four-arm run with no title gate and
the phase-5 + arm-width predicate. A complete valid table selects fog/grid/
aspect by score ordering; any arm still failing its gate selects only the
remaining route failure.

Competing hypotheses:

- H-title-gate: removing the title predicate yields valid captures without
  changing runtime behavior.
- H-edge-fog: dd2 changes edge excess relative to retail; combined follows dd2.
- H-edge-grid: dd2 and combined share the edge signature.
- H-edge-aspect: aspect-only and combined share the edge signature.

Exact command: update the helper, run `zsh scratch/agent/s6394_edge_arms.sh`,
then run `python3 tools/g3c_edge_score.py` on each gated `fbd` directory. Do
not change runtime defaults or visual code.
