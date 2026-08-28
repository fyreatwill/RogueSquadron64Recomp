# NEXT work unit — classify `0x80040218`

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Competing hypotheses and discriminator

- `H-exact-companion-name`: the address has an exact companion identity that
  can be synchronized.
- `H-data-gap-or-fragment`: the entry is not a named standalone function in
  the companion project; retain the placeholder or classify it as a gap only
  if independent boundaries support that conclusion.
- `H-overlay-collision`: more than one generated callable definition or
  conflicting registration exists and requires manual review.

The discriminating measurement is one bounded static audit: compare the
companion symbol/m2c sources, generated body and boundaries, all generated
callers, overlay registration, and duplicate definitions for `0x80040218`.
An exact companion name plus one coherent callable selects synchronization; a
complete but unnamed callable selects no invented rename; a boundary-only
fragment or collision selects a documented non-rename/manual review.

The preceding `0x8003E8DC` audit selected the exact rename
`slotDispatcherIter`; its companion and generated callable boundaries were
coherent. Do not revisit it without new source evidence.

## Exact commands

```sh
rg -n '80040218|func_80040218' ../rogue_squadron64 ../N64Recomp/RecompiledFuncs syms tools/rename
rg -n -C 20 '80040218|func_80040218' ../N64Recomp/RecompiledFuncs/funcs_*.c
python3 tools/sweep_scan_candidates.py func_80040218
```

If the sources agree on an exact identity, synchronize the project symbol
TOML and build `cmake --build build --config Debug --target RecompiledFuncs`.
If they do not, leave the placeholder unchanged, record the evidence, and
build nothing beyond any required static checks. Do not modify audio or route
behavior.

## Open dependency

M5 still needs a new route repair or independent handoff that reaches title
and hangar. The s2993 C628 probe passed its same-run task controls but stayed
pre-title, so its target null was unevaluable; retain that dependency for a
future genuinely new route angle.
