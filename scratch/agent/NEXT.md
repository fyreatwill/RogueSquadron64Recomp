# NEXT work unit (s1266)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Do not build or run. Perform one bounded exact-name census over the next adjacent generated-symbol region, `0x80084AE8..0x8008588C`. Record every entry's address, size, generated definition, companion name/source, caller evidence, and confidence before editing. Synchronize only exact independent names in `syms/rogue_squadron.syms.toml`; leave address-encoded and explicitly fake entries unchanged.

Competing hypotheses and discriminator:

- H1: the region has exact independent companion mappings, so the coherent subset can be synchronized.
- H2: mappings are partial or ambiguous, so only an exact subset is safe and the remainder stays address-encoded.
- H3: no independent naming source exists and the region should be parked.

The discriminator is the complete comparison table: full exact coverage selects H1, a safe exact subset selects H2, and no independent names selects H3. No runtime mitigation or experiment is justified.

Exact commands:

```
rg -n '80084AE8|80084B08|80084B28|80084B48|80084BC8|8008588C' ../rogue_squadron64/symbol_files/main_overlay.txt syms/rogue_squadron.syms.toml ../N64Recomp/RecompiledFuncs/funcs_20.c
rg -n -C 3 '80084AE8|80084B08|80084B28|80084B48|80084BC8|8008588C' ../rogue_squadron64/symbol_files/main_overlay.txt
rg -n '80084AE8|80084B08|80084B28|80084B48|80084BC8|8008588C' ../N64Recomp/RecompiledFuncs/funcs_20.c ../N64Recomp/RecompiledFuncs/funcs_*.c
```
