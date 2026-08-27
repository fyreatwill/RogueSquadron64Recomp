# Session 2544 generated-symbol census

## Region table

| placeholder | complete span | decoded body | companion evidence | result |
|---|---|---|---|---|
| `fake_func_800AE3E4` | `0x800AE3E4–0x800AE3EF` (12 bytes) | `lwc1 f0,0x58(fp)`; `lwc1 f2,0xC4(fp)`; `mul.s f0,f0,f2`; no prologue, return, jump, or complete callable body | `mission_overlay.txt` retains the fake at `0x800AE3E4`; generated declaration and `recomp_overlays.inl` agree; `initPlayerCraftTrailBuffers` follows at `0x800AE3F0`; the menu overlay independently registers `tickEasedCameraKeyframeBlend` at the overlapping `0x800AE3EC`, overlapping the byte range in a different overlay | unchanged; `H-data-boundary` / `H-no-match` |

## Discriminator

The complete generated span, companion symbol inputs, overlay registrations,
and exact-address source/m2c/caller searches were checked. No exact human
mapping exists. The overlap with a separately registered menu-overlay entry
and the absence of a callable boundary make renaming this fragment to either
neighbor speculative. This selects the boundary classification over
`H-named-match`; no generated code or symbol input changed.
