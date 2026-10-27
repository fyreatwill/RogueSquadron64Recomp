# NEXT: phase-align the completed G3c(a) edge table
HYPOTHESIS-ID: g3c-edge-arm-route-gate

Use the completed s6396 logs and dumps, or rerun the same helper if needed, but
score only comparable flight-phase dumps: retail/dd2 at `width=640`,
aspect/combined at `width=796`, after the phase-5 witness. Keep title/armed rows
informational; retain positive framebuffer-hash/terrain controls and zero
crash/stall checks. The helper fixes from s6396 are already in place.

DISCRIMINATING MEASUREMENT: one table of four phase-aligned edge scores. If dd2
tracks combined while aspect tracks retail, select grid; if dd2 tracks retail
while combined tracks aspect, select fog; if aspect and combined share the shift
against both controls, select aspect. Any missing arm is a route/capture failure,
not visual evidence.

Competing hypotheses:

- H-title-gate: fixed; the clean rerun reached all four mission predicates.
- H-edge-fog: dd2 changes edge excess relative to retail; combined follows dd2.
- H-edge-grid: dd2 and combined share the edge signature.
- H-edge-aspect: aspect-only and combined share the edge signature.

Exact command: use `python3 tools/g3c_edge_score.py` on phase-aligned flight
windows in each `scratch/agent/m6/g1_lvl1s6394_*/fbd` directory. Do not change
runtime defaults or visual code.
