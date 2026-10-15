# Generated-symbol rename audit — Session 5025

The companion repository's new menu-overlay mapping was checked against the
current generated snapshot before being added to the regeneration helper.

| gate | evidence | result |
|---|---|---|
| semantic mapping | `rogue_squadron64/symbol_files/menu_overlay.txt` maps `buildLevelSelectTextTextures` to `0x800B3824` | pass |
| generated identity | `RecompiledFuncs/funcs_30.c` starts the body at `0x800B3824`; the prior generated name in the sibling diff was `func_800B3824` | pass |
| exact span | `recomp_overlays.inl` records offset `0x0000E6F4` and ROM size `0x2D8`; the next record begins at `0x800B3AFC` | pass |
| live caller | `funcs_31.c` calls `buildLevelSelectTextTextures` at the existing call site | pass |

The mapping is therefore regeneration-safe and was added to
`tools/rename_generated_symbols.py`. No generated files, runtime code, or
submodule contents were changed.
