# NEXT work unit (s1822)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume leftover `func_800ECDDC`. Last-15 ledger titles after
s1821 still include the s1808 revisit (`selected H2 menuIn/mission
jal-sites`), so the 15-title all-sweep REVISIT gate does not fire.

Census leftover `func_800ECDDC` (`0x800ECDDC`, size `0x28`).
Neighbor peek already: companion `mission_overlay.txt` maps
`dispatchSlotActionTwelveByGlobalId = 0x800ECDDC`; no
`main_overlay.txt` occupant. Generated `funcs.h` / `funcs_40.c` /
overlay INL already `dispatchSlotActionTwelveByGlobalId`. TOML still
`{ name = "func_800ECDDC", vram = 0x800ECDDC, size = 0x28 }`.
Previous occupant is now `craftMountedAnimationNpcHandler`
(`0x800ECC28`, `0x1B4`; s1821 synchronized) then this wrapper.
First insn `addiu $sp, $sp, -0x18`; last live `jr $ra` /
`addiu $sp, $sp, 0x18` at `0x800ECDFC` / `0x800ECE00`. One
generated `jal 0x800ECDDC` inside `tickMissionObjectives` at
`0x800FBD18` already dispatches the human name. The body loads
the global id from `lhu 0x8013959C` (`lui 0x8014` /
`-0x6A64`), sets `a1 = 0xC`, and jals `slotDispatcherIter` at
`0x800ECDF0`. Next occupant is leftover `fake_func_800ECE04`
(`0x800ECE04`, `0xC`).

Competing hypotheses:

- H1: already synchronized — TOML, generated headers/body, overlay
  INL, and companion already agree on one human name with matching
  size (confirm only; no rename).
- H2: one or more sources still carry stale `func_800ECDDC`.
  Companion `mission_overlay.txt` already has
  `dispatchSlotActionTwelveByGlobalId`. Rename the stale sources to
  that companion name (do not invent a name) only if the live body
  is the action-0xC dispatcher wrapper. If the live body does
  not match that role, leave the leftover and do not steal the name.
- H3: leftover splat, overlay collision, or size/boundary
  disagreement (`craftMountedAnimationNpcHandler` ends at
  `0x800ECDDC`; generated next occupant is
  `fake_func_800ECE04` at `0x800ECE04`). Do not invent a name.
- H4: companion, generated body, TOML, or section-4 row is missing.

Exact commands (no game run):

```
# TOML + generated + overlay INL
grep -n '800ECDDC\|func_800ECDDC\|dispatchSlotActionTwelveByGlobalId\|800ECE04\|fake_func_800ECE04' \
  syms/rogue_squadron.syms.toml \
  ../N64Recomp/RecompiledFuncs/funcs.h \
  ../N64Recomp/RecompiledFuncs/recomp_overlays.inl
# generated body + callers
grep -n 'func_800ECDDC\|dispatchSlotActionTwelveByGlobalId\|jal         0x800ECDDC' \
  ../N64Recomp/RecompiledFuncs/funcs_4*.c
# companion overlays
grep -n '800ECDDC\|func_800ECDDC\|dispatchSlotActionTwelveByGlobalId\|800ECE04\|fake_func_800ECE04' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/*.txt
```

Then read the generated body: `addiu $sp, $sp, -0x18` at
`0x800ECDDC`; `lhu` global id from `0x8013959C`; `a1 = 0xC`;
`jal slotDispatcherIter` at `0x800ECDF0`. Classify against the
companion name; do not invent a name.

Expected splits:

- H1: all four sources already `dispatchSlotActionTwelveByGlobalId`
  (or another agreed human name) at size `0x28`. Confirm.
- H2: rename the stale `func_800ECDDC` placeholder(s) to
  `dispatchSlotActionTwelveByGlobalId` (TOML and/or generated
  headers/body/INL and/or jal sites) if the body matches.
- H3: document the leftover/collision/size miss; leave the name.
- H4: fill the missing source or leave as `func_*`.

Do not reopen the s1744 six-entry, s1760 jump-table, s1776
main-text, s1792 unwatched-caller, or s1808 jal/`prev_pc` Rice
recipes. The next 15-title REVISIT is the M4 accumulator
boundary, not another `submitGfxFrame` PC set.
