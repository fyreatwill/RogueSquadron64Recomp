# NEXT work unit (s1011)

s1010 (static semantic audit): GLideN64's TriGen paths copy colorData into
vertex RGBA, but retail/generated `L_1740` writes record `+0x18` from `v6`,
whose producer is the transformed-vector path. RT64 decodes the later RDP
shade coefficient block at the expected post-position offset. This selects
`H-missing-lighting-source`; no mitigation was made.

HYPOTHESIS-ID: m4-zero-shade-emission-constant

## One work unit

Trace the `v6` producer through the `L_16B8` mode bit and the DMEM constants
loaded from `0x60`. Static audit only; no build/run required. Do not edit
generated output.

Competing hypotheses and discriminating measurement:

- `H-v6-clip-predicate`: `v6` is a clip/test vector and `+0x18` is being
  populated from the wrong register class.
- `H-v6-lighting-result`: `v6` is the intended lighting/fog result, and the
  sentinel is caused by a specific mode or constant path.
- `H-v6-mode-misread`: the `L_16B8` branch or DMEM constant interpretation is
  wrong in the generated/runtime model.

Discriminator: identify every producer of `v6` on both sides of `L_16B8`,
decode the DMEM `0x60` vector values and the branch's mode bit, and compare
their role with the reference's explicit RGBA color path. A clip/test-only
producer selects `H-v6-clip-predicate`; a documented lighting/fog vector with
sentinel-producing constants selects `H-v6-lighting-result`; a mismatch in
branch/constant semantics selects `H-v6-mode-misread`.

The `slotDispatcherIter` sp-guard soak crashed at a different site before
producing a guard record; it remains a separate queued investigation and is
not this work unit.
