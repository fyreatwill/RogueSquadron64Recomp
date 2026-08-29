# NEXT work unit — audit remaining VI request handoffs

HYPOTHESIS-ID: m5-retail-video-publication-boundary

## Single work unit

Audit all remaining callers of `requestViFeatureChange` in the generated tree
(`0x80044BAC`, `0x800AFA70`, `0x800AF644`, `0x800B42BC`, and `0x800ADB34`),
using bounded source windows and caller/argument provenance. Produce one
short audit artifact that chooses the highest-information-value retail PC for
the next oracle run. Do not instrument or build the port in this unit.

## Competing hypotheses

- H-RemainingCaller: one of the five callers is executed at the 640-to-1024
  transition and hands off the missing publication state.
- H-AlreadyEnumerated: all five are pre-title or post-publication requests;
  the writer is outside `requestViFeatureChange` callers.
- H-Ambiguous: static provenance cannot distinguish a target-phase caller;
  the next useful probe must move to a different handoff family.

## Discriminating measurement

The discriminating measurement is the complete caller classification table:
an identified target-phase caller with a concrete argument and path to the
pending word selects H-RemainingCaller; only pre-title/post-publication
callers selects H-AlreadyEnumerated; unresolved phase/provenance selects
H-Ambiguous. The prior oracle run is the independent negative control for
`0x800C2984`: it fired once at 640 pre-title, while the whole-RDRAM control
and title/hangar phase controls passed.

## Exact run requirements

Read the generated callers and the relevant `requestViFeatureChange` body in
bounded windows; record caller phase, argument source, and whether the edge
can reach the pending-word store. Do not modify the port or repeat the closed
`0x800C2984`, `0x8001A098:0x8001BB6C`, or selector/helper watches.
