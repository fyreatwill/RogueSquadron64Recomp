# NEXT work unit (s1547)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

s1546 synchronized `cinematicInterpRatio` at `0x800AF668` and left
already-fake `fake_func_800AF6A8` unchanged. Resume the
generated-symbol renaming sweep. Perform exactly one bounded
exact-name census over the next adjacent generated function,
`0x800AFCF4..0x800AFE4C`.
Do not build or run. Record its address, size, generated definition,
companion name/source, caller or semantic evidence, and confidence
before editing. Synchronize only an exact independent name in
`syms/rogue_squadron.syms.toml`; leave address-encoded, fake, or
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
table, not a function), `func_8009D978` unchanged (s1478:
eight-byte PC-relative Q15 delay-mix table, not a function), and
`fake_func_800AF6A8` unchanged (s1546 H2: already-fake cinematic
overlay data-tail gap-filler). The generated entry at this address
is already `findNearestSceneObjectToPoint`; the companion mission
list maps `findNearestSceneObjectToPoint = 0x800AFCF4`. TOML is
still `func_800AFCF4` (size `0x158`, ends at generated
`loadPlayerStartPosition` / TOML `func_800AFE4C` at `0x800AFE4C`).
Overlay `rom_size` is `0x158` at offset `0x0000ABC4`. Confirm the
complete live function, matching size, and caller/semantic evidence
before synchronizing the TOML name. Independently named
`tickCutsceneObject` at `0x800AF04C` (`rom_size` `0xCA8`) ends at
this address. Last live instruction pair is `0x800AFE44`/`0x800AFE48`
(`jr $ra` / `addiu $sp, $sp, 0x48`). Cinematic-overlay data
(`cutsceneTypeStrings` at `0x800AF6B0`, `gCutsceneIdMappingTable`
at `0x800AF7B4`) occupies overlapping VRAM from `.ovl.cinematic`
and is not a mission size split. Menu-overlay
`tickCraftSelectScreen` / TOML `func_800AF3C0` at `0x800AF3C0`
(`rom_size` `0x2EC`, ends `0x800AF6AC`) occupies a different
overlay window that ends before this address.

Any future oracle/M4 watch must use Homebrew Rice
`--video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib`
with the eleven-Start schedule (s1496). Post-hangar extra A or extra
Start reaches 640/`0x6a2900` (s1528). Dummy video stays at 320.
Do not re-watch `0x688:0x710` (s1512 H2). s1544: 640 is resident
menu-overlay, not mission/cinematic/hangar-tick; post-settle Start/B
do not advance.

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
grep -n -C 5 '800AFCF4\|800AFE4C\|findNearestSceneObjectToPoint' ../rogue_squadron64/symbol_files/mission_overlay.txt
grep -n -C 4 '800AFCF4\|800AFE4C\|findNearestSceneObjectToPoint' ../N64Recomp/RecompiledFuncs/funcs_29.c
grep -n -C 3 '800AFCF4\|800AFE4C' syms/rogue_squadron.syms.toml
```
