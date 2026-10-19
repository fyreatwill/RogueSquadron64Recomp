# Generated-symbol audit — Session 5574

Candidate: `fake_func_800AE3E4`

## Discriminator

| Surface | Evidence | Result |
|---|---|---|
| Generated recomp | `funcs_28.c` emits a `0xC`-byte record at `0x800AE3E4`, containing `lwc1` at `+0`, `lwc1` at `+4`, and `mul.s` at `+8`; the next generated body starts at `0x800AE3EC` | Split/fragment, not a standalone callable body |
| Companion map | `mission_overlay.txt` retains `fake_func_800AE3E4 = 0x800AE3E4` and starts `initPlayerCraftTrailBuffers` at `0x800AE3F0` | No semantic name for the candidate |
| Independent syms | `syms/rogue_squadron.syms.toml` assigns `fake_func_800AE3E4` size `0xC` and `initPlayerCraftTrailBuffers` at `0x800AE3F0` | Exact 12-byte placeholder span agrees |
| Cross-overlay context | `menu_overlay.txt` names `tickEasedCameraKeyframeBlend` at `0x800AE3EC` | The overlapping instruction boundary is overlay/split context, not evidence for a mission rename |

## Decision

H2 selected. The record is a defined non-callable/data-gap fragment and has no
companion-backed semantic mission name. It remains unchanged. The existing
regeneration-safe mapping in `tools/rename_generated_symbols.py` already maps
it to `data_gap_800AE3E4`; no generated output or runtime code was edited.

