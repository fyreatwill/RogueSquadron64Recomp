# Session 3085 audit: `0x8006ACA4`

## Hypotheses and discriminator

- H-ExactIdentity: the six independent surfaces establish a callable semantic name.
- H-Fragment: the record is an inline fragment or boundary with no distinct callable identity.
- H-Conflict: address, extent, overlay, or companion surfaces disagree.
- H-Unresolved: the available surfaces cannot classify it.

The discriminator is the six-surface agreement table below. A callable body
with matching callers and independent mappings would select H-ExactIdentity;
an instruction-only body without callers selects H-Fragment; disagreement
selects H-Conflict; missing surfaces select H-Unresolved.

## Six-surface table

| Surface | Observation | Result |
|---|---|---|
| Companion map | `main_overlay.txt` retains `fake_func_8006ACA4 = 0x8006ACA4`; it assigns no semantic name. | No exact identity |
| Generated body | `funcs_16.c` has only `lwc1`, `lwc1`, and `add.s` at `0x8006ACA4..0x8006ACAC`; no prologue or return. | Fragment |
| Callers | No generated `jal 0x8006ACA4` or symbolic caller reference. | Not callable |
| Header | The generated declaration was the placeholder record. | Consistent with fragment |
| Overlay registration | Main overlay records exactly 12 bytes at offset `0x6A864`, immediately before `transformObjectColliderCenter`. | Boundary extent confirmed |
| Project TOML | The prior 12-byte placeholder record sits between `transformMeshPartIntoWorld` and `transformObjectColliderCenter`. | Mechanical mapping only |

## Decision

H-Fragment selected. The record is renamed mechanically to
`data_gap_8006ACA4` in the project TOML, rename tooling, generated body,
header, and overlay registration. The companion map remains untouched because
it has no independent semantic identity to synchronize.

ORIGIN: naming-only classification. No runtime, route, audio, mitigation, or
generated instruction behavior changed.
