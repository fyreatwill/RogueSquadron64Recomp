# NEXT work unit (s1545)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

s1544 was the mandatory every-15-sessions revisit (Rice 640-identity:
menu overlay stays resident; not mission/cinematic/hangar-tick;
post-settle Start/B do not advance). Resume the generated-symbol
renaming sweep. Perform exactly one bounded exact-name census over
the next adjacent generated function, `0x800AF65C..0x800AF668`.
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
table, not a function), and `func_8009D978` unchanged (s1478:
eight-byte PC-relative Q15 delay-mix table, not a function). The
generated entry at this address is already `getCinematicStateSubObject`;
the companion cinematic list maps `getCinematicStateSubObject = 0x800AF65C`.
TOML is still `func_800AF65C` (size `0xC`, ends at independently
named generated `cinematicInterpRatio` / TOML `func_800AF668` at
`0x800AF668`). Overlay `rom_size` is `0xC` at offset `0x0000A52C`.
Confirm the complete live function, matching size, and caller/semantic
evidence before synchronizing the TOML name. Independently named
`cinematicDeactivator` at `0x800AF60C` (`rom_size` `0x50`) ends at
this address. The generated body is `lw $v0, 0xC($a0)` / `jr $ra` /
`nop`. Last live instruction pair is `0x800AF660`/`0x800AF664`
(`jr $ra` / `nop`). Generated callers include independently named
`setupCutsceneLevel` (`0x800A6E08`, `0x800A6F04`, `0x800A6F24`,
`0x800A6F40`), `computeCutsceneScreenScale` (`0x800AD25C`,
`0x800AD310`, `0x800AD3A4`), and
`tickCutsceneCameraFromTimeline` (`0x800AD6BC`). Menu-overlay
`tickCraftSelectScreen` / TOML `func_800AF3C0` at `0x800AF3C0`
(`rom_size` `0x2EC`, ends `0x800AF6AC`) occupies overlapping VRAM
and is a different overlay, not a cinematic size split.
Mission-overlay `tickCutsceneObject` at `0x800AF04C` continues
`playCutsceneObjectImpactSound` / TOML `func_800AEF58` at
`0x800AEF58` (size `0xF4`, ends `0x800AF04C`) and likewise overlaps
from `.ovl.mission`.

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
grep -n -C 5 '800AF65C\|800AF668\|getCinematicStateSubObject' ../rogue_squadron64/symbol_files/cinematic_overlay.txt
grep -n -C 4 '800AF65C\|800AF668\|getCinematicStateSubObject' ../N64Recomp/RecompiledFuncs/funcs_29.c
grep -n -C 3 '800AF65C\|800AF668' syms/rogue_squadron.syms.toml
```
