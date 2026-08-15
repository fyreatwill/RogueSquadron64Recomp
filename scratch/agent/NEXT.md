# NEXT work unit (s1271)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Perform exactly one bounded exact-name census over the next adjacent generated
symbol region, `0x80086FC4..0x800880D8`. Do not build or run. Record each
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
rg -n '80086FC4|800873D4|800878D0|80087D90|80087EE8|80088068|800880D8' ../rogue_squadron64/symbol_files/main_overlay.txt syms/rogue_squadron.syms.toml ../N64Recomp/RecompiledFuncs/funcs_21.c
rg -n -C 3 '80086FC4|800873D4|800878D0|80087D90|80087EE8|80088068|800880D8' ../rogue_squadron64/symbol_files/main_overlay.txt
rg -n '80086FC4|800873D4|800878D0|80087D90|80087EE8|80088068|800880D8' ../N64Recomp/RecompiledFuncs/funcs_21.c ../N64Recomp/RecompiledFuncs/funcs_*.c
```
