# Session 5027 rename audit

The next bounded menu-overlay candidate is `buildScaledFormatTextElement` at
`0x800B3AFC`.

| Gate | Evidence | Result |
| --- | --- | --- |
| semantic mapping | `rogue_squadron64/symbol_files/menu_overlay.txt` maps the name to `0x800B3AFC` | pass |
| generated identity and span | `RecompiledFuncs/funcs_30.c` starts the body at `0x800B3AFC`; `recomp_overlays.inl` records offset `0xE9CC` and span `0x174` | pass |
| live caller | `funcs_29.c` and `funcs_31.c` call the function; the companion `menuControllerInput` decomp also calls `func_800B3AFC` | pass |

The regeneration helper now preserves `func_800B3AFC` as
`buildScaledFormatTextElement`. No runtime or patch behavior changed.
