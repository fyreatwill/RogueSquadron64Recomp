# NEXT work unit (s1521)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

s1520 synchronized `getAssetNameForNpcType` at `0x800AE98C`.
Resume the generated-symbol renaming sweep. Perform exactly one bounded
exact-name census over the next adjacent generated function,
`0x800AEA18..0x800AEA28`. Do not build or run. Record its address, size,
generated definition, companion name/source, caller or semantic evidence,
and confidence before editing. Synchronize only an exact independent name
in `syms/rogue_squadron.syms.toml`; leave address-encoded, fake, or
ambiguous entries unchanged. Leave `func_8008ED6C` unchanged
(s1309 H2), `func_800927B0` unchanged (s1355 H3), `func_80092A54`
unchanged (s1357 H3), `func_80092CF0` unchanged (s1359 H3),
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
one-instruction `mtc1 $zero, $f4` fragment),
`func_8009D8BC` unchanged (s1477: eight-byte PC-relative packed-nibble
table, not a function), and `func_8009D978` unchanged (s1478:
eight-byte PC-relative Q15 delay-mix table, not a function). The
generated entry at this address is already `getCutsceneRuntimeContext`;
the companion cinematic list maps `getCutsceneRuntimeContext = 0x800AEA18`.
TOML is still `func_800AEA18` (size `0x10`, ends at independently named
`cuts_0058_bubble_sort` at `0x800AEA28`). Overlay `rom_size` is `0x10`
at offset `0x000098E8`. Confirm the complete live function, matching
size, and caller/semantic evidence before synchronizing the TOML name.
Companion `main_overlay.txt` notes independently named
`isNpcWithinActiveReferenceRange` at `0x80047D40` calls `func_800AEA18`
when scene byte `0x80130B39` is nonzero (cinematic camera). Menu-overlay
`hangarLoadShadows` at `0x800AE9E0` (`rom_size` `0xE0`, ends
`0x800AEAC0`) occupies overlapping VRAM and is a different overlay, not
a cinematic size split. Mission-overlay `playRandomCutsceneVoiceLine` /
TOML `func_800AE960` at `0x800AE960` (size `0x398`) likewise overlaps
from `.ovl.mission`.

Any future oracle/M4 watch must use Homebrew Rice
`--video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib`
with the eleven-Start schedule (s1496). Dummy video stays at 320.
Do not re-watch `0x688:0x710` (s1512 H2).

Competing hypotheses and discriminator:

- H1: the function has an exact independent companion mapping and can be
  synchronized (or is already synchronized under that exact name).
- H2: the mapping is partial, already-fake, or ambiguous, so the entry
  must remain unchanged.
- H3: no independent naming source exists and the region should be parked.

The complete comparison table is the discriminator: an exact companion
name with matching generated/TOML live-body size and semantic or caller
evidence selects H1; an incomplete, already-fake, or conflicting match
selects H2; and no independent name selects H3.

Commands:

```
grep -n -C 5 '800AEA18\|800AEA28\|getCutsceneRuntimeContext' ../rogue_squadron64/symbol_files/cinematic_overlay.txt
grep -n -C 4 '800AEA18\|800AEA28\|getCutsceneRuntimeContext' ../N64Recomp/RecompiledFuncs/funcs_29.c
grep -n -C 3 '800AEA18\|800AEA28' syms/rogue_squadron.syms.toml
```
