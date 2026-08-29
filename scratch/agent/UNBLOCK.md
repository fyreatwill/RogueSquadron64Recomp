# Unblock result — Session 3215

Route 3 — re-scoped the work unit.

Route 1 was checked against the oracle help, oracle README, route-related
source, and all locally documented M5 route knobs. The oracle's Rice video
plugin is present, but it only proves the independent retail route; it does
not make the current port arm reach target phase.

Route 2 was tested locally on the current build:

- `run_s2618_hangar_pcm_boundary.sh`: image and silent arms both passed the
  dispatch and host-boundary controls, then stopped at VI 640,
  `0x0066A500`; title/hangar counts were zero and crash/abort counts were zero.
- the retained eleven-Start image recipe: dispatch reached 1,280 sampled rows
  and the image arm passed the host control, but it also stopped at VI 640,
  `0x0066A500`, with no title/hangar transition.

The M5 dependency is therefore real for the target-phase measurement: a
human-selected route or new retail-grounded boundary is still needed. Route 3
keeps the loop moving with a bounded static M3 audit of the 3D voice-list
writer/publication and traversal invariant, which does not require title or
hangar reachability.
