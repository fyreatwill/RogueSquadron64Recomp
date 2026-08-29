# NEXT work unit — retail boundary for the next VI publication handoff family

HYPOTHESIS-ID: m5-retail-video-publication-boundary

## Single work unit

Use `scratch/agent/s3119_m5_vi_request_callers.md` to move the independent
retail oracle to the next unenumerated handoff family: attribute the first
write/call after the pending request-mask store and before the VI descriptor
changes from 640 to 1024. Build one watch set containing the whole-RDRAM
positive control, title/hangar phase controls, and the complete candidate PC
range; do not repeat `0x800C2984`, `0x8001A098:0x8001BB6C`, or the closed
selector/helper range. Do not instrument or build the port in this unit.

## Competing hypotheses

- H-NextHandoff: a retail-attributed store/call between the request-mask write
  and descriptor publication identifies the missing writer boundary.
- H-OutsideInterval: the descriptor changes through a writer outside the
  watched interval, so the next probe must widen to the descriptor consumer or
  VI register handoff.
- H-NoTransition: the retail run reaches title without a directly attributable
  descriptor write in either family, indicating a deferred/frame-boundary
  publication path.

## Discriminating measurement

The discriminating measurement is the PC-attributed write/call sequence across
the 640→1024 transition. A candidate in the interval with a matching
descriptor write selects H-NextHandoff; no candidate but a descriptor write in
the widened consumer handoff selects H-OutsideInterval; no descriptor write
with passed phase controls selects H-NoTransition. The prior oracle run is the independent negative control for
`0x800C2984`: it fired once at 640 pre-title, while the whole-RDRAM control
and title/hangar phase controls passed.

## Exact run requirements

Read the generated callers and the relevant `requestViFeatureChange` body in
bounded windows; record caller phase, argument source, and whether the edge
can reach the pending-word store. Do not modify the port or repeat the closed
`0x800C2984`, `0x8001A098:0x8001BB6C`, or selector/helper watches.
