# NEXT work unit — audit `0x8000DE70`

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Competing hypotheses and discriminator

- `H-exact-companion-name`: the generated entry at `0x8000DE70` has an exact
  human identity in the companion map and can be synchronized.
- `H-ambiguous-placeholder`: the generated body or call context does not
  support that name; leave the placeholder and record why.
- `H-overlay-collision`: the address has multiple generated definitions, so it
  requires manual review rather than an automatic rename.

The discriminating measurement is one bounded static audit: compare the
companion map, generated definition, and all generated callers for
`0x8000DE70`, then check for duplicate generated definitions. An exact map
match plus a unique callable definition and coherent caller use selects the
rename; any missing or conflicting source selects no-op/manual review. No
runtime phase or route repair is required.

## Exact commands

```sh
rg -n '8000DE70|func_8000DE70' ../rogue_squadron64 ../N64Recomp/RecompiledFuncs
python3 tools/sweep_scan_candidates.py func_8000DE70
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
