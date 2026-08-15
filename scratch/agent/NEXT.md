# NEXT work unit (s1317)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Perform exactly one bounded exact-name census over the next adjacent generated
function, `0x8008F95C..0x8008F9C8`. Do not build or run. Record its address,
size, generated definition, companion name/source, caller or semantic evidence,
and confidence before editing. Synchronize only an exact independent name in
`syms/rogue_squadron.syms.toml`; leave address-encoded, fake, or ambiguous
entries unchanged. Leave `func_8008ED6C` unchanged (s1309 H2).

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
rg -n -C 5 '8008F95C|8008F9C8' ../rogue_squadron64/symbol_files/main_overlay.txt
rg -n -C 4 '8008F95C|8008F9C8' ../N64Recomp/RecompiledFuncs/funcs_23.c
rg -n -C 3 '8008F95C|8008F9C8' syms/rogue_squadron.syms.toml
```
