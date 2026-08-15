# NEXT work unit (s1401)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Perform exactly one bounded exact-name census over the next adjacent generated
function, `0x800964C8..0x80096540`. Do not build or run. Record its address,
size, generated definition, companion name/source, caller or semantic evidence,
and confidence before editing. Synchronize only an exact independent name in
`syms/rogue_squadron.syms.toml`; leave address-encoded, fake, or ambiguous
entries unchanged. Leave `func_8008ED6C` unchanged (s1309 H2),
`func_800927B0` unchanged (s1355 H3), `func_80092A54` unchanged
(s1357 H3), `func_80092CF0` unchanged (s1359 H3),
`func_80092F10` unchanged (s1360: TOML-only live-tail fragment),
`fake_func_80093E74` unchanged (s1369: already-fake epilogue fragment),
and `fake_func_80094348` unchanged (s1378: already-fake two-instruction
jump fragment).

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
grep -n -C 5 '800964C8\|80096540' ../rogue_squadron64/symbol_files/main_overlay.txt
grep -n -C 4 '800964C8\|80096540' ../N64Recomp/RecompiledFuncs/funcs_25.c
grep -n -C 3 '800964C8\|80096540' syms/rogue_squadron.syms.toml
```
