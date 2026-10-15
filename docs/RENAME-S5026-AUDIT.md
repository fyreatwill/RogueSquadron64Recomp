# Generated-symbol rename audit — Session 5026

The companion menu-overlay mapping for `0x800B2630` was checked against the
generated snapshot and added to the regeneration helper.

| gate | evidence | result |
|---|---|---|
| semantic mapping | `rogue_squadron64/symbol_files/menu_overlay.txt` maps `buildFormatMessageGlyphBuffer` to `0x800B2630` | pass |
| generated identity | `RecompiledFuncs/funcs_30.c` starts the body at `0x800B2630` | pass |
| exact span | `recomp_overlays.inl` records ROM size `0x468`; the next record starts at `0x800B2A98` | pass |
| live caller | `funcs_30.c` calls it from `0x800B369C`, `0x800B3B54`, and `0x800B3C8C` | pass |

The mapping is regeneration-safe. The generated snapshot was already
synchronized, so this change only makes the rename explicit and persistent in
`tools/rename_generated_symbols.py`.
