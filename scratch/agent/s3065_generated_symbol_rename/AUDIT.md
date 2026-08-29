# Session 3065 — `0x800B47C4`

## Discriminator

The six-surface comparison distinguishes an exact semantic preamble from a
boundary-only fragment or metadata drift. A callable body would need its own
return/control-flow shape and callers; a fragment may be named only when an
adjacent routine and independent companion evidence identify its role.

## Surface comparison

| Surface | Evidence | Result |
|---|---|---|
| Companion symbol map | `menu_overlay.txt` retains `fake_func_800B47C4` at `0x800B47C4`; its nearby comment identifies `menuControllerInput` at `0x800B47D0` and describes the 12-byte record as a fake splat trampoline preceding the real body | Boundary is deliberate; companion map does not yet carry the semantic preamble name |
| Companion source/docs | `docs/controller_stuff/func_800B47C4.c` is the large menu/controller routine; `menus.md` and `controller_stuff.md` describe that routine as menu/controller input, matching the adjacent generated body rather than the 12-byte record | Role of the adjacent body is independently established |
| Generated body | `funcs_31.c` decodes `0x800B47C4..0x800B47CC` as `lui`, `lwc1`, `swc1`, then ends; `menuControllerInput` begins at `0x800B47D0` and spans `0x38E4` bytes | The target is a non-callable preamble, not a second full function |
| Generated callers | `menuOverlayInit` calls `0x800B47D0`; no generated caller targets `0x800B47C4` | Confirms the callable entry is `menuControllerInput`, not the target record |
| Header/overlay registration | `funcs.h` declares both records; `recomp_overlays.inl` registers the target at offset `0xF694`, size `0xC`, followed by `menuControllerInput` at `0xF6A0`, size `0x38E4` | Extents and ordering agree exactly |
| Project metadata/local tooling | TOML had the stale placeholder at `0x800B47C4`; both rename maps already map it to `menuControllerInputPreamble` | Synchronize TOML; no mapping drift remains |

## Decision

Selected `H-ExactIdentity` for the bounded semantic fragment name
`menuControllerInputPreamble`. This is not a rename of the large callable
routine: its exact generated entry remains `menuControllerInput` at
`0x800B47D0`. The 12-byte record is named from two independent lines of
evidence: its exact adjacency/extent to the established menu-input body and
the existing regeneration-safe rename maps that classify this kind of splat
prefix as a preamble. No runtime build or run was needed for this static unit.

