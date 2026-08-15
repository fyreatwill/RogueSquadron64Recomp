# NEXT work unit (s1265)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Do not build or run. Perform one bounded exact-name census over the next adjacent generated-symbol region, `0x80083EF4..0x80084860`. Record every entry's address, size, generated definition, companion name/source, caller evidence, and confidence before editing. Synchronize only exact independent names in `syms/rogue_squadron.syms.toml`; leave address-encoded and explicitly fake entries unchanged.

Competing hypotheses and discriminator:

- H1: the region has exact independent companion mappings, so the coherent subset can be synchronized.
- H2: mappings are partial or ambiguous, so only an exact subset is safe and the remainder stays address-encoded.
- H3: no independent naming source exists and the region should be parked.

The discriminator is the complete comparison table: full exact coverage selects H1, a safe exact subset selects H2, and no independent names selects H3. No runtime mitigation or experiment is justified.

Exact commands:

```
rg -n '80083EF4|80083F3C|80084510|800847A4|80084860' ../rogue_squadron64/symbol_files/main_overlay.txt syms/rogue_squadron.syms.toml ../N64Recomp/RecompiledFuncs/funcs_20.c
rg -n -C 3 '80083EF4|80083F3C|80084510|800847A4|80084860' ../rogue_squadron64/symbol_files/main_overlay.txt
rg -n '80083EF4|80083F3C|80084510|800847A4|80084860' ../N64Recomp/RecompiledFuncs/funcs_20.c ../N64Recomp/RecompiledFuncs/funcs_*.c
```
