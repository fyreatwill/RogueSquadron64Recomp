# NEXT work unit (s1279)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Perform exactly one bounded exact-name census over the next adjacent generated
symbol region, `0x8008AE50..0x8008B284`. Do not build or run. Record each
entry's address, size, generated definition, companion name/source, caller or
semantic evidence, and confidence before editing. Synchronize only exact
independent names in `syms/rogue_squadron.syms.toml`; leave address-encoded,
fake, or ambiguous entries unchanged.

Competing hypotheses and discriminator:

- H1: all five entries have exact independent companion mappings, so the
  coherent subset can be synchronized.
- H2: mappings are partial or ambiguous, so only an exact subset is safe and
  the remainder stays address-encoded.
- H3: no independent naming source exists and the region should be parked.

The complete comparison table is the discriminator: full exact coverage
selects H1, a safe exact subset selects H2, and no independent names selects
H3. The current reconnaissance suggests H2 may apply because the companion
file names `0x8008B284` while the generated definition is not present; verify
that rather than assuming the mapping is usable.

Commands:

```
rg -n -C 4 '8008AE50|8008B0A8|8008B254|8008B26C|8008B284' ../rogue_squadron64/symbol_files/main_overlay.txt
rg -n -C 3 '8008AE50|8008B0A8|8008B254|8008B26C|8008B284' ../N64Recomp/RecompiledFuncs/funcs_22.c
rg -n -C 2 '8008AE50|8008B0A8|8008B254|8008B26C|8008B284' syms/rogue_squadron.syms.toml
```
