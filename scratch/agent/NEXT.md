# NEXT work unit (s1281)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Perform exactly one bounded exact-name census over the next adjacent generated
symbol region, `0x8008B9CC..0x8008BA60`. Do not build or run. Record each
entry's address, size, generated definition, companion name/source, caller or
semantic evidence, and confidence before editing. Synchronize only exact
independent names in `syms/rogue_squadron.syms.toml`; leave address-encoded,
fake, or ambiguous entries unchanged.

Competing hypotheses and discriminator:

- H1: both entries have exact independent companion mappings, so both can be
  synchronized.
- H2: mappings are partial or ambiguous, so only an exact subset is safe and
  the remainder stays address-encoded.
- H3: no independent naming source exists and the region should be parked.

The complete comparison table is the discriminator: full exact coverage
selects H1, a safe exact subset selects H2, and no independent names selects
H3.

Commands:

```
rg -n -C 4 '8008B9CC|8008BA60' ../rogue_squadron64/symbol_files/main_overlay.txt
rg -n -C 3 '8008B9CC|8008BA60' ../N64Recomp/RecompiledFuncs/funcs_23.c
rg -n -C 2 '8008B9CC|8008BA60' syms/rogue_squadron.syms.toml
```
