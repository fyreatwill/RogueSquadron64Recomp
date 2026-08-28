# Session 3007 source table — `0x80017B28`

| Source | Finding |
|---|---|
| `../rogue_squadron64/symbol_files/main_overlay.txt:2813` | Exact companion identity: `setViewStateTripletBytes = 0x80017B28`. |
| `../N64Recomp/RecompiledFuncs/funcs_4.c:29518` | Unique generated callable definition is already named `setViewStateTripletBytes`; body stores `$a0`, `$a1`, and `$a2` into the adjacent view-state bytes and returns `1`. |
| `../N64Recomp/RecompiledFuncs/funcs_36.c:18614` | One direct generated caller at `0x800CA6AC`, calling `setViewStateTripletBytes`. |
| `../N64Recomp/RecompiledFuncs/funcs.h:224` | Header declaration already uses `setViewStateTripletBytes`. |
| `../N64Recomp/RecompiledFuncs/recomp_overlays.inl:225` | Overlay registration already uses `setViewStateTripletBytes`, size `0x20`. |
| `syms/rogue_squadron.syms.toml:236` | Only stale artifact: placeholder `func_80017B28`, size `0x20`. |

Duplicate check: `rg` found one generated `RECOMP_FUNC` definition and one
generated `jal` reference. The sweep helper's overlay-reuse warning does not
indicate duplicate callable definitions.

Result: synchronize the project TOML to `setViewStateTripletBytes`; build
`RecompiledFuncs` passed at 100%.
