# Session 3006 — `0x80017AE0`

## Discriminating audit

| Source | Result |
|---|---|
| Companion symbol map | `setViewStateBytesAndFadeScale = 0x80017AE0` |
| Generated definition | One `RECOMP_FUNC` definition in `../N64Recomp/RecompiledFuncs/funcs_4.c`, size `0x48`; body writes selector bytes and a fade-scale value to the `0x8012A873`–`0x8012A87C` state region and returns `1` |
| Generated callers | Two direct callers, at `0x80044914` and `0x800CA47C`, both invoke the same generated entry with a stack float argument |
| Header/overlay registration | `setViewStateBytesAndFadeScale` is present in `funcs.h` and `recomp_overlays.inl` |
| Duplicate definition check | One generated callable definition; no duplicate definition found |

The companion identity, generated body, and caller set agree. The project
symbol TOML was stale and was synchronized to `setViewStateBytesAndFadeScale`.
`cmake --build build --config Debug --target RecompiledFuncs` passed.

Commands used:

```sh
rg -n '80017AE0|func_80017AE0' ../rogue_squadron64 ../N64Recomp/RecompiledFuncs
python3 tools/sweep_scan_candidates.py func_80017AE0
cmake --build build --config Debug --target RecompiledFuncs
```
