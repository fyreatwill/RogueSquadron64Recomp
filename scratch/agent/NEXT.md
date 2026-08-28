# NEXT work unit — synchronize coalesceFreeHeapBlocks

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Competing hypotheses and discriminator

- `H-exact-companion-name`: the companion symbol map's
  `coalesceFreeHeapBlocks` is the semantic name for generated entry
  `0x800022F8`; synchronize it into the project TOML.
- `H-ambiguous-placeholder`: the generated body or call context does not
  support that name; leave the placeholder and record why.
- `H-overlay-collision`: the address has multiple generated definitions, so
  it requires manual review rather than an automatic rename.

The discriminating measurement is one bounded static audit: compare the
companion map, generated definition, and all generated callers for
`0x800022F8`, then check for duplicate generated definitions. An exact map
match plus a unique callable definition and coherent caller use selects the
rename; any missing or conflicting source selects no-op/manual review. No
runtime phase or route repair is required.

## Exact commands

```sh
rg -n '800022F8|func_800022F8|coalesceFreeHeapBlocks' \
  ../rogue_squadron64 ../N64Recomp/RecompiledFuncs
python3 tools/sweep_scan_candidates.py func_800022F8
```

If the three-source check agrees, update `syms/rogue_squadron.syms.toml`,
build `cmake --build build --config Debug --target RecompiledFuncs`, and
record the result. Do not invent a name for an ambiguous fragment and do not
modify audio or route behavior while the M5 route dependency remains open.

## Open dependency

M5 still needs a new route repair or independent handoff that reaches title
and hangar. The s2993 C628 probe passed its same-run task controls but stayed
pre-title, so its target null was unevaluable; retain that dependency for a
future genuinely new route angle.
