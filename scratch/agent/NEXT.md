# NEXT work unit (s1274)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Perform exactly one bounded exact-name census over the next adjacent generated
symbol region, `0x80089414..0x800897D4`. Do not build or run. Record each
entry's address, size, generated definition, companion name/source, caller or
semantic evidence, and confidence before editing. Synchronize only exact
independent names in `syms/rogue_squadron.syms.toml`; leave address-encoded,
fake, or ambiguous entries unchanged.

Competing hypotheses and discriminator:

- H1: the region has exact independent companion mappings, so the coherent
  subset can be synchronized.
- H2: mappings are partial or ambiguous, so only an exact subset is safe and
  the remainder stays address-encoded.
- H3: no independent naming source exists and the region should be parked.

The complete comparison table is the discriminator: full exact coverage
selects H1, a safe exact subset selects H2, and no independent names selects
H3. No runtime mitigation or experiment is justified.

Commands:

```
rg -n '80089414|800894F0|80089548|80089558|800895BC|80089774|80089798|800897D4' ../rogue_squadron64/symbol_files/main_overlay.txt syms/rogue_squadron.syms.toml ../N64Recomp/RecompiledFuncs/funcs_21.c ../N64Recomp/RecompiledFuncs/funcs_*.c
rg -n -C 3 '80089414|800894F0|80089548|80089558|800895BC|80089774|80089798|800897D4' ../rogue_squadron64/symbol_files/main_overlay.txt
```
