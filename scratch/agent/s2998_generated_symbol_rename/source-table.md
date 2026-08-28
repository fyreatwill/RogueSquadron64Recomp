# Session 2998 symbol audit — `0x8000C07C`

| Source | Result |
|---|---|
| Companion map | `submitGfxFrame = 0x8000C07C`, documented as the per-frame graphics orchestrator. |
| Generated definition | One callable definition in `RecompiledFuncs/funcs_3.c`, already named `submitGfxFrame`; body performs the expected frame-submit sequence. |
| Generated callers | 14 direct `jal 0x8000C07C` sites across the generated tree. |
| Overlay registration | One `submitGfxFrame` entry at overlay offset `0xBC3C`, size `0x674`. |
| Duplicate definition check | No second `RECOMP_FUNC` definition. |
| Project TOML before audit | Stale placeholder `func_8000C07C`. |
| Change | Renamed the TOML entry to `submitGfxFrame`; `RecompiledFuncs` target built successfully. |

The three-source identity and unique generated definition select the exact
companion-name hypothesis. No runtime, audio, or route behavior changed.
