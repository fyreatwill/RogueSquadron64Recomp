# NEXT work unit (s1478)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Perform exactly one bounded exact-name census over the next adjacent generated
function, `0x8009D8C4..0x8009D980`. Do not build or run. Record its address,
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
gap), `fake_func_80099FDC` unchanged (s1451 H2: already-fake
one-word `bne` gap before `aspMainTextStart`),
`fake_func_8009C2C8` unchanged (s1471 H2: already-fake
two-instruction COP1 multiply-accumulate fragment),
`fake_func_8009D7CC` unchanged (s1476 H2: already-fake
one-instruction `mtc1 $zero, $f4` fragment), and
`func_8009D8BC` unchanged (s1477: eight-byte PC-relative packed-nibble
table, not a function). The generated entry at this address is already
`applyVoiceDelayFilter`; the companion splat list maps
`applyVoiceDelayFilter = 0x8009D8C4`. TOML is still `func_8009D8C4`
(size `0xB4`, ends at `0x8009D978`); overlay `rom_size` is `0xBC` and
lumps the eight-byte `func_8009D978` pad before independently named
`runVoiceLatticeFilter` at `0x8009D980`. Confirm the complete function,
matching size, and caller/semantic evidence before synchronizing the
TOML name. Classify the `0x8009D978` pad in the same table; do not
invent a name for it.

Competing hypotheses and discriminator:

- H1: the function has an exact independent companion mapping and can be
  synchronized (or is already synchronized under that exact name).
- H2: the mapping is partial, already-fake, or ambiguous, so the entry must
  remain unchanged.
- H3: no independent naming source exists and the region should be parked.

The complete comparison table is the discriminator: an exact companion name
with matching generated/TOML size and semantic or caller evidence selects H1;
an incomplete, already-fake, or conflicting match selects H2; and no
independent name selects H3.

Commands:

```
grep -n -C 5 '8009D8C4\|8009D978\|8009D980\|applyVoiceDelayFilter\|runVoiceLatticeFilter' ../rogue_squadron64/symbol_files/main_overlay.txt
grep -n -C 4 '8009D8C4\|8009D978\|applyVoiceDelayFilter' ../N64Recomp/RecompiledFuncs/funcs_27.c
grep -n -C 3 '8009D8C4\|8009D978\|8009D980' syms/rogue_squadron.syms.toml
```
