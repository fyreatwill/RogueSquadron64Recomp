# Session 3117 static audit: retail VI handoff

## Candidate

The new boundary is guest PC `0x800C2984`, inside
`runMenuModelViewerScreen` (`0x800C28F0`, size `0x518`). Its delay-slot
constant at `0x800C2988` sets `$a0 = 0x11`, then the call reaches
`requestViFeatureChange` at `0x8001B7B8`.

The callee stores that request at `0x80128E90` (`0x80130000 - 0x7170`),
the pending feature/mode word. This is a producer-side handoff into the
existing pending-change path, not one of the already closed direct
`osViSetMode` callsites or the `selectAndApplyViMode` range.

## Static evidence

The call is reached after `load_hmt_and_hob`, `walkMeshdef0List`, and
`applyFlagsToMeshTreeOrList`, immediately before the function begins its
mode-dependent setup. The request argument is an immediate constant, so the
oracle can attribute the event to this exact guest PC without reconstructing
host return addresses. The callee's first store is the pending-word write;
there is no framebuffer or VI-register write at this boundary.

The current generated tree contains six callers of `requestViFeatureChange`.
The other relevant static edges are `0x80044BAC` (data-derived argument),
`0x800AFA70` (constant `1`), `0x800AF644` (constant `8`),
`0x800B42BC` (constant `8`), and `0x800ADB34` (data-derived argument).
`0x800C2984` is the only newly selected menu-model edge because its caller
and constant are both identified and it sits outside the already watched
producer callsites.

## Discriminating oracle measurement

Watch the physical PC for `0x800C2984` plus the whole-RDRAM positive control,
and retain title/hangar VI phase controls. A hit at the 640-to-1024
transition, followed by the pending-word write and the later title phase,
supports `H-NewHandoff`. Hits only during an already-published target phase,
with no transition-time hit, support `H-ExistingConsumer`. No hit while the
whole-RDRAM control and title/hangar controls pass supports `H-DeadOrAliased`.

This is a boundary test, not a runtime change. It does not by itself identify
the final VI-mode writer or justify changing audio or VI behavior.
