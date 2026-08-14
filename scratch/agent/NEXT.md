# NEXT work unit (s1011)

s1010 (static semantic audit): GLideN64's TriGen paths copy colorData into
vertex RGBA, but retail/generated `L_1740` writes record `+0x18` from `v6`,
whose producer is the transformed-vector path. RT64 decodes the later RDP
shade coefficient block at the expected post-position offset. This selects
`H-missing-lighting-source`; no mitigation was made.

HYPOTHESIS-ID: m4-zero-shade-emission-constant

## One work unit

Explain the numeric `-0.5/+0.5` sentinel from the final `vge` compare,
tracing the lane semantics of `v4`, `v0`, and `v29[1q]` against an independent
RSP semantic reference. Static audit only; no build/run required. Do not edit
generated output.

Competing hypotheses and discriminating measurement:

- `H-vge-sentinel-encoding`: the RSP `vge` result naturally encodes the
  observed fixed `-0.5/+0.5` coefficients after RT64's shade decode.
- `H-v4-v0-source`: one operand lane is a fixed compare/clip source, producing
  the sentinel before `vge`.
- `H-shade-store-interpretation`: the compare result is ordinary, but the
  downstream shade coefficient interpretation maps its predicate bits to the
  sentinel.

Discriminator: decode the exact `vge` lane result and RT64 coefficient mapping
for the observed sentinel. A reference that produces the same sentinel from
the compare selects `H-vge-sentinel-encoding`; a fixed operand selects
`H-v4-v0-source`; a mismatch only after the RDP/RT64 store selects
`H-shade-store-interpretation`.

The `slotDispatcherIter` sp-guard soak crashed at a different site before
producing a guard record; it remains a separate queued investigation and is
not this work unit.
