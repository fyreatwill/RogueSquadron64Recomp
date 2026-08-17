# NEXT work unit (s1820)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume leftover `func_800EC6F0`. Last-15 ledger titles after
s1819 still include the s1808 revisit (`selected H2 menuIn/mission
jal-sites`), so the 15-title all-sweep REVISIT gate does not fire.

Census leftover `func_800EC6F0` (`0x800EC6F0`, size `0x538`).
Neighbor peek already: companion `mission_overlay.txt` still
`func_800EC6F0 = 0x800EC6F0`; `main_overlay.txt` maps
`tickCraftMountedAnimationEffect = 0x800EC6F0` (comment: s415
reverted from mission_overlay, bisection split tested in
isolation). Generated `funcs.h` / `funcs_40.c` / overlay INL still
`func_800EC6F0`. TOML still
`{ name = "func_800EC6F0", vram = 0x800EC6F0, size = 0x538 }`.
Previous leftover is now `destroyObjectOwnedNpcSlot`
(`0x800EC6C0`, `0x2C`; s1819 synchronized) then already-named
`fake_func_800EC6EC` (`0x800EC6EC`, `0x4`). First insn
`addiu $sp, $sp, -0xA0`; last live `jr $ra` / `addiu $sp, $sp, 0xA0`
at `0x800ECC20` / `0x800ECC24`. `lbu +0x4C`; `mtc1 $a1, $f20`;
`lwc1 +0x48` then `add.s`. Three jals: `findActiveNpcInSlotChain`
(`0x8003FC28`) at `0x800EC780`, `getNpcContextField8`
(`0x8004015C`) at `0x800EC798`, `tickObjectSoundCueState`
(`0x800EF510`) at `0x800ECBF0`. Sole generated `jal 0x800EC6F0`
is inside `craftMountedAnimationNpcHandler` at `0x800ECD90`.
Next occupant is leftover `func_800ECC28` / generated
`craftMountedAnimationNpcHandler` (`0x800ECC28`, `0x1B4`).

Competing hypotheses:

- H1: already synchronized — TOML, generated headers/body, overlay
  INL, and companion already agree on one human name with matching
  size (confirm only; no rename).
- H2: one or more sources still carry stale `func_800EC6F0`.
  Companion `main_overlay.txt` already has
  `tickCraftMountedAnimationEffect`. Rename the stale sources to
  that companion name (do not invent a name) only if the live body
  is the craft-mounted animation tick that
  `craftMountedAnimationNpcHandler` calls. If the live body does
  not match that role, leave the leftover and do not steal the name.
- H3: leftover splat, overlay collision, or size/boundary
  disagreement (`fake_func_800EC6EC` ends at `0x800EC6F0`;
  generated next occupant is `craftMountedAnimationNpcHandler` at
  `0x800ECC28`). The main_overlay name is an s415 revert from
  mission — treat a mission leftover + main alias as a collision
  unless the generated body is the mission occupant and no other
  function claims `0x800EC6F0`. Do not invent a name.
- H4: companion, generated body, TOML, or section-4 row is missing.

Exact commands (no game run):

```
# TOML + generated + overlay INL
grep -n '800EC6F0\|func_800EC6F0\|tickCraftMountedAnimationEffect\|800ECC28\|craftMountedAnimationNpcHandler' \
  syms/rogue_squadron.syms.toml \
  ../N64Recomp/RecompiledFuncs/funcs.h \
  ../N64Recomp/RecompiledFuncs/recomp_overlays.inl
# generated body + callers
grep -n 'func_800EC6F0\|tickCraftMountedAnimationEffect\|jal         0x800EC6F0' \
  ../N64Recomp/RecompiledFuncs/funcs_4*.c
# companion overlays
grep -n '800EC6F0\|func_800EC6F0\|tickCraftMountedAnimationEffect\|800ECC28\|craftMountedAnimationNpcHandler' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/*.txt
```

Then read the generated body: `lbu +0x4C` at `0x800EC70C`;
`findActiveNpcInSlotChain` at `0x800EC780`; `getNpcContextField8`
at `0x800EC798`; `tickObjectSoundCueState` at `0x800ECBF0`.
Classify against the companion name; do not invent a name.

Expected splits:

- H1: all four sources already `tickCraftMountedAnimationEffect`
  (or another agreed human name) at size `0x538`. Confirm.
- H2: rename the stale `func_800EC6F0` placeholder(s) to
  `tickCraftMountedAnimationEffect` (TOML and/or generated
  headers/body/INL and/or jal sites) if the body matches.
- H3: document the leftover/collision/size miss; leave the name.
- H4: fill the missing source or leave as `func_*`.

Do not reopen the s1744 six-entry, s1760 jump-table, s1776
main-text, s1792 unwatched-caller, or s1808 jal/`prev_pc` Rice
recipes. The next 15-title REVISIT is the M4 accumulator
boundary, not another `submitGfxFrame` PC set.
