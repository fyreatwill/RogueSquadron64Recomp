# NEXT work unit (s1360)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Perform exactly one bounded exact-name census over the next adjacent generated
function, `0x80092E48..0x80092F94`. Do not build or run. Record its address,
size, generated definition, companion name/source, caller or semantic evidence,
and confidence before editing. Synchronize only an exact independent name in
`syms/rogue_squadron.syms.toml`; leave address-encoded, fake, or ambiguous
entries unchanged. Leave `func_8008ED6C` unchanged (s1309 H2),
`func_800927B0` unchanged (s1355 H3), `func_80092A54` unchanged
(s1357 H3), and `func_80092CF0` unchanged (s1359 H3).

Competing hypotheses and discriminator:

- H1: the function has an exact independent companion mapping and can be
  synchronized.
- H2: the mapping is partial or ambiguous, so the address-encoded entry must
  remain unchanged.
- H3: no independent naming source exists and the region should be parked.

The complete comparison table is the discriminator: an exact companion name
with matching generated/TOML size and semantic or caller evidence selects H1;
an incomplete or conflicting match selects H2; and no independent name selects
H3.

Commands:

```
grep -n -C 5 '80092E48\|80092F94' ../rogue_squadron64/symbol_files/main_overlay.txt
grep -n -C 4 '80092E48\|80092F94' ../N64Recomp/RecompiledFuncs/funcs_24.c
grep -n -C 3 '80092E48\|80092F94' syms/rogue_squadron.syms.toml
```
