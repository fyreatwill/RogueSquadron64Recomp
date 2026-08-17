# NEXT work unit (s1821)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume leftover `func_800ECC28`. Last-15 ledger titles after
s1820 still include the s1808 revisit (`selected H2 menuIn/mission
jal-sites`), so the 15-title all-sweep REVISIT gate does not fire.

Census leftover `func_800ECC28` (`0x800ECC28`, size `0x1B4`).
Neighbor peek already: companion `mission_overlay.txt` maps
`craftMountedAnimationNpcHandler = 0x800ECC28`; no
`main_overlay.txt` occupant. Generated `funcs.h` / `funcs_40.c` /
overlay INL already `craftMountedAnimationNpcHandler`. TOML still
`{ name = "func_800ECC28", vram = 0x800ECC28, size = 0x1B4 }`.
Previous occupant is now `tickCraftMountedAnimationEffect`
(`0x800EC6F0`, `0x538`; s1820 synchronized) then this handler.
First insn `addiu $sp, $sp, -0x18`; last live `jr $ra` /
`addiu $sp, $sp, 0x18` at `0x800ECDD4` / `0x800ECDD8`. No
generated `jal 0x800ECC28` (NPC-handler table dispatch). The
handler's tick path jals `tickCraftMountedAnimationEffect` at
`0x800ECD90`, then `destroyNpcSlotByIndex` at `0x800ECDAC` when
that tick returns 1. Next occupant is leftover `func_800ECDDC` /
generated `dispatchSlotActionTwelveByGlobalId` (`0x800ECDDC`,
`0x28`).

Competing hypotheses:

- H1: already synchronized — TOML, generated headers/body, overlay
  INL, and companion already agree on one human name with matching
  size (confirm only; no rename).
- H2: one or more sources still carry stale `func_800ECC28`.
  Companion `mission_overlay.txt` already has
  `craftMountedAnimationNpcHandler`. Rename the stale sources to
  that companion name (do not invent a name) only if the live body
  is the craft-mounted animation NPC handler. If the live body does
  not match that role, leave the leftover and do not steal the name.
- H3: leftover splat, overlay collision, or size/boundary
  disagreement (`tickCraftMountedAnimationEffect` ends at
  `0x800ECC28`; generated next occupant is
  `dispatchSlotActionTwelveByGlobalId` at `0x800ECDDC`). Do not
  invent a name.
- H4: companion, generated body, TOML, or section-4 row is missing.

Exact commands (no game run):

```
# TOML + generated + overlay INL
grep -n '800ECC28\|func_800ECC28\|craftMountedAnimationNpcHandler\|800ECDDC\|dispatchSlotActionTwelveByGlobalId' \
  syms/rogue_squadron.syms.toml \
  ../N64Recomp/RecompiledFuncs/funcs.h \
  ../N64Recomp/RecompiledFuncs/recomp_overlays.inl
# generated body + callers
grep -n 'func_800ECC28\|craftMountedAnimationNpcHandler\|jal         0x800ECC28' \
  ../N64Recomp/RecompiledFuncs/funcs_4*.c
# companion overlays
grep -n '800ECC28\|func_800ECC28\|craftMountedAnimationNpcHandler\|800ECDDC\|dispatchSlotActionTwelveByGlobalId' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/*.txt
```

Then read the generated body: `addiu $sp, $sp, -0x18` at
`0x800ECC28`; action-1 spawn clears child `+0x48/+0x4C/+0x4D` and
looks up the craft spatial grid at `0x801375D8+0x34`; tick path
jals `tickCraftMountedAnimationEffect` at `0x800ECD90`. Classify
against the companion name; do not invent a name.

Expected splits:

- H1: all four sources already `craftMountedAnimationNpcHandler`
  (or another agreed human name) at size `0x1B4`. Confirm.
- H2: rename the stale `func_800ECC28` placeholder(s) to
  `craftMountedAnimationNpcHandler` (TOML and/or generated
  headers/body/INL and/or jal sites) if the body matches.
- H3: document the leftover/collision/size miss; leave the name.
- H4: fill the missing source or leave as `func_*`.

Do not reopen the s1744 six-entry, s1760 jump-table, s1776
main-text, s1792 unwatched-caller, or s1808 jal/`prev_pc` Rice
recipes. The next 15-title REVISIT is the M4 accumulator
boundary, not another `submitGfxFrame` PC set.
