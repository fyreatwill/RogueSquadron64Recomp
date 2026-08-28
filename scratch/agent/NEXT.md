# NEXT work unit (s2947) — route qualification pivot before M5 candidate match

HYPOTHESIS-ID: m5-route-qualification-repair

M5 remains the strategic priority, but s2946 could not qualify the port route.
Do one new route-qualification experiment before interpreting the candidate:
run the documented autopilot recipe with the route-transition controls that
previously distinguished pre-title `0x0066A500` from title/hangar, and capture
route prepare/VI commit/fetch controls in one run. Do not change behavior or
de-stub audio in this unit.

## Competing hypotheses and discriminator

- H-RouteReachesTarget: the repaired route reaches title/hangar and permits the
  candidate match.
- H-RoutePreTitle: route controls fire but the port still stops at pre-title
  640, so candidate matching remains blocked.
- H-RouteInstrumentGap: the route reaches a target origin but one required
  route/fetch control is absent, invalidating the comparison.

The discriminator is one same-run table of VI origin/width, route-prepare
accepted state, route ordinal, `[f5-fetch-control]`, and candidate rows. Target
origin plus all controls selects H-RouteReachesTarget; pre-title origin with
controls selects H-RoutePreTitle; a missing required control selects
H-RouteInstrumentGap.

## Exact work

Use the existing route-transition probe and autopilot; keep every route field
in one build/run. Run the Debug binary from `build/` with the established
180 s recipe and capture the result in a new `scratch/agent/s2947_*` artifact.
