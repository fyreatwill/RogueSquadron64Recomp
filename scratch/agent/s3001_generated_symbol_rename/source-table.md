# Session 3001 — `0x8000E0BC`

| Source | Finding |
| --- | --- |
| Companion symbol map | `selectRenderPresetByIndex` at `0x8000E0BC` in `main_overlay.txt`. |
| Project symbol TOML | Already synchronized as `selectRenderPresetByIndex`, size `0x24`. |
| Generated definition | One definition in `RecompiledFuncs/funcs_3.c`; masks an 8-bit index, loads the render preset table entry, stores it at `0x8011A258`, and returns `1`. |
| Generated callers | Ten direct call sites across `funcs_27.c`, `funcs_31.c`, `funcs_33.c`, `funcs_36.c`, and `funcs_42.c`; all call the same generated entry with index `0` or `1`. |
| Duplicate check | Exactly one `RECOMP_FUNC void selectRenderPresetByIndex(...)` definition tree-wide. |
| Build | `cmake --build build --config Debug --target RecompiledFuncs` passed. |

The exact companion identity is confirmed, but no rename was needed because
the project TOML, generated header, and overlay registration were already
synchronized before this audit. The placeholder-only sweep scanner reported
the expected tooling limitation because `func_8000E0BC` is no longer in the
TOML.
