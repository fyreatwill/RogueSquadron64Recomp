# NEXT work unit (s1282)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Perform exactly one bounded exact-name census over the next adjacent generated
function, `0x8008BC10..0x8008C9AC`. Do not build or run. Record its address,
size, generated definition, companion name/source, caller or semantic
evidence, and confidence before editing. Synchronize only an exact independent
name in `syms/rogue_squadron.syms.toml`; leave address-encoded, fake, or
ambiguous entries unchanged.

Competing hypotheses and discriminator:

- H1: the function has an exact independent companion mapping and can be
  synchronized.
- H2: the mapping is partial or ambiguous, so the address-encoded entry must
  remain unchanged.
- H3: no independent naming source exists and the region should be parked.

The complete comparison table is the discriminator: an exact companion name
with matching generated/TOML size and semantic or caller evidence selects H1;
an incomplete or conflicting match selects H2; and no independent name
selects H3.

Commands:

```
rg -n -C 5 '8008BC10|8008C9AC' ../rogue_squadron64/symbol_files/main_overlay.txt
rg -n -C 4 '8008BC10|8008C9AC' ../N64Recomp/RecompiledFuncs/funcs_23.c
rg -n -C 3 '8008BC10|8008C9AC' syms/rogue_squadron.syms.toml
```
