# s2595 generated-symbol census: `0x800CC038`

## Discriminator table

| Evidence | Result |
|---|---|
| Generated entry | `fake_func_800CC038` in `RecompiledFuncs/funcs_37.c`; one complete `swc1 $f0, 0x40($fp)` at `0x800CC038` |
| Following generated body | `initActorFromSpawnTemplate` starts at `0x800CC03C`; its first instruction is the overlapping `addiu $v0, $fp, 0x20` delay/entry boundary |
| Companion symbol table | `fake_func_800CC038 = 0x800CC038`; no semantic name; `loadMedalInfo` begins at `0x800CC040` |
| Exact-address source/m2c/caller search | No independent source body, m2c body, caller alias, or alternate semantic symbol found |
| Rename coverage | `build_redefs.py` completed; no `800CC038` line emitted. Neighboring semantic mappings were emitted for `0x800CC02C`, `0x800CC03C`, and `0x800CC040` |

## Verdict

`H-BoundaryOnly` selected. The placeholder remains unchanged because the
companion explicitly retains it and the generated span has no defensible
semantic identity. The `swc1` is likely a fragment associated with the
adjacent function boundary, but adjacency alone is not sufficient for a
rename.
