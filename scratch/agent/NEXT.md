# NEXT work unit (s1453)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Perform exactly one bounded exact-name census over the next adjacent generated
function, `0x8009B048..0x8009B268`. Do not build or run. Record its address,
size, generated definition, companion name/source, caller or semantic evidence,
and confidence before editing. Synchronize only an exact independent name in
`syms/rogue_squadron.syms.toml`; leave address-encoded, fake, or ambiguous
entries unchanged. Leave `func_8008ED6C` unchanged (s1309 H2),
`func_800927B0` unchanged (s1355 H3), `func_80092A54` unchanged
(s1357 H3), `func_80092CF0` unchanged (s1359 H3),
`func_80092F10` unchanged (s1360: TOML-only live-tail fragment),
`fake_func_80093E74` unchanged (s1369: already-fake epilogue fragment),
`fake_func_80094348` unchanged (s1378: already-fake two-instruction
jump fragment), `fake_func_8009711C` unchanged (s1408: already-fake
one-instruction jump fragment), `fake_func_80097D58` unchanged
(s1420: already-fake two-instruction epilogue fragment),
`fake_func_80099C4C` unchanged (s1446 H2: already-fake one-word `beq`
gap), and `fake_func_80099FDC` unchanged (s1451 H2: already-fake
one-word `bne` gap before `aspMainTextStart`). The generated entry at
this address is already `allocAndConfigureNewVoice`; synchronize the
stale TOML `func_8009B048` only if the companion, size, and
caller/semantic evidence independently support that exact name.

Competing hypotheses and discriminator:

- H1: the function has an exact independent companion mapping and can be
  synchronized.
- H2: the mapping is partial, already-fake, or ambiguous, so the entry must
  remain unchanged.
- H3: no independent naming source exists and the region should be parked.

The complete comparison table is the discriminator: an exact companion name
with matching generated/TOML size and semantic or caller evidence selects H1;
an incomplete, already-fake, or conflicting match selects H2; and no
independent name selects H3.

Commands:

```
grep -n -C 5 '8009B048\|8009B268\|allocAndConfigureNewVoice' ../rogue_squadron64/symbol_files/main_overlay.txt
grep -n -C 4 '8009B048\|8009B268' ../N64Recomp/RecompiledFuncs/funcs_26.c
grep -n -C 3 '8009B048\|8009B268' syms/rogue_squadron.syms.toml
```
