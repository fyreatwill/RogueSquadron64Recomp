# NEXT work unit (s1571)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

s1570 parked already-fake `fake_func_800B42BC` at `0x800B42BC` (H2).
Resume the generated-symbol renaming sweep.
Perform exactly one bounded exact-name census over the next adjacent
generated function, `0x800B42C0..0x800B4588`.
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
eight-byte PC-relative Q15 delay-mix table, not a function),
`fake_func_800AF6A8` unchanged (s1546 H2: already-fake cinematic
overlay data-tail gap-filler), and `fake_func_800B42BC` unchanged
(s1570 H2: already-fake one-instruction `lw $v0, 0x2C($fp)` gap).
TOML is already `playerXwingInit` (size `0x2C8`). Overlay `rom_size`
is `0x2C8` at offset `0x0000F190`. Companion mission list maps
`playerXwingInit = 0x800B42C0`. Generated `funcs_31.c` starts
`addiu $sp, $sp, -0x50` and ends `jr $ra` / `addiu $sp, $sp, 0x50`
at `0x800B4580` / `0x800B4584`. Confirm the already-named function
before leaving the entry unchanged. Independently named (parked)
`fake_func_800B42BC` at `0x800B42BC` (`rom_size` `0x4`) ends at this
address. Independently named `playWeaponFireSound` at `0x800B4588`
(TOML still `func_800B4588`, `rom_size` `0x738`) starts at the next
word. Two generated `jal 0x800B42C0` sites live in
`playerXwingUpdate`. This naming census does not reopen closed M5
audio de-stubbing.

Any future oracle/M4 watch must use Homebrew Rice
`--video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib`
with the eleven-Start schedule (s1496). Post-hangar extra A or extra
Start reaches 640/`0x6a2900` (s1528). That 640 is `runModelViewerLoop`
(s1569); extra Start during it does not exit. Dummy video stays at 320.
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
grep -n -C 5 '800B42C0\|800B4588\|playerXwingInit\|playWeaponFireSound' ../rogue_squadron64/symbol_files/mission_overlay.txt
grep -n -C 4 '800B42C0\|playerXwingInit' ../N64Recomp/RecompiledFuncs/funcs_31.c
grep -n -C 3 '800B42C0\|800B4588\|playerXwingInit' syms/rogue_squadron.syms.toml
```
