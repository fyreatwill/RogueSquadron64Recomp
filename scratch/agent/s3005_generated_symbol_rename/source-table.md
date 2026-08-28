# Session 3005 — `0x80017AC0`

The bounded audit compared the companion map, generated tree, project TOML,
header, overlay registration, and direct callers.

| Check | Result |
|---|---|
| Companion identity | `setRenderStateFlagByteTwo` at `0x80017AC0`; the map describes the adjacent single-byte render-state setter. |
| Generated definition | One definition in `../N64Recomp/RecompiledFuncs/funcs_4.c`; stores `a0` at `0x8012A871` and returns `1`. |
| Generated callers | Five direct callers at `0x800530BC`, `0x800AEE6C`, `0x800C2E7C`, `0x800C4054`, and `0x800A737C`. |
| Header/overlay | `funcs.h` and `recomp_overlays.inl` already use `setRenderStateFlagByteTwo`. |
| Duplicate check | No duplicate callable definition; the scanner warning is overlay reference/registration reuse. |
| Validation | `cmake --build build --config Debug --target RecompiledFuncs` passed. |

The stale project TOML entry was synchronized to `setRenderStateFlagByteTwo`.
No runtime behavior was changed.
