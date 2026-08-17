# NEXT work unit (s1818)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume leftover `func_800EC684`. Last-15 ledger titles after
s1817 still include the s1808 revisit (`selected H2 menuIn/mission
jal-sites`), so the 15-title all-sweep REVISIT gate does not fire.

Census leftover `func_800EC684` (`0x800EC684`, size `0x3C`).
Neighbor peek already: companion `mission_overlay.txt` maps
`clearPendingAndDestroyChildNpc = 0x800EC684`; generated `funcs.h`
/ `funcs_40.c` / overlay INL already say
`clearPendingAndDestroyChildNpc`; TOML still
`{ name = "func_800EC684", vram = 0x800EC684, size = 0x3C }`.
Previous leftover is now `createAndInitObject` (`0x800EC588`,
`0xFC`; s1817 synchronized). First insn `addiu $sp, $sp, -0x18`;
last live `jr $ra` / `addiu $sp, $sp, 0x18` at `0x800EC6B8` /
`0x800EC6BC`. `jal clearPendingChildNpc` (`0x800F2A24`) at
`0x800EC698`; `jal unlinkAndFreeChildNpcNode` (`0x800EC388`) at
`0x800EC6A4`; always returns 1. Companion lists 17 named callers;
generated has 20 `jal 0x800EC684` sites (16 in `funcs_36.c`–
`funcs_39.c` plus 4 in `funcs_18.c`/`funcs_19.c`). Next occupant
is `destroyObjectOwnedNpcSlot` (`0x800EC6C0`, `0x2C`; generated
already named; TOML still `func_800EC6C0`).

Competing hypotheses:

- H1: already synchronized — TOML, generated headers/body, overlay
  INL, and companion already agree on `clearPendingAndDestroyChildNpc`
  with matching size (confirm only; no rename).
- H2: one or more sources still carry stale `func_800EC684`.
  Companion and generated already have `clearPendingAndDestroyChildNpc`.
  Rename the stale sources to that companion name (do not invent
  a name). If the live body does not clear the pending child and
  unlink/free the node, leave the leftover and do not steal the name.
- H3: leftover splat, overlay collision, or size/boundary
  disagreement (previous `createAndInitObject` ends at `0x800EC684`;
  generated next occupant is `destroyObjectOwnedNpcSlot` at
  `0x800EC6C0`). Do not invent a name.
- H4: companion, generated body, TOML, or section-4 row is missing.

Exact commands (no game run):

```
# TOML + generated + overlay INL
grep -n '800EC684\|func_800EC684\|clearPendingAndDestroyChildNpc\|800EC6C0\|destroyObjectOwnedNpcSlot' \
  syms/rogue_squadron.syms.toml \
  ../N64Recomp/RecompiledFuncs/funcs.h \
  ../N64Recomp/RecompiledFuncs/recomp_overlays.inl
# generated body + callers
grep -n 'func_800EC684\|clearPendingAndDestroyChildNpc\|jal         0x800EC684' \
  ../N64Recomp/RecompiledFuncs/funcs_1*.c \
  ../N64Recomp/RecompiledFuncs/funcs_3*.c \
  ../N64Recomp/RecompiledFuncs/funcs_4*.c
# companion overlays
grep -n '800EC684\|func_800EC684\|clearPendingAndDestroyChildNpc\|800EC6C0\|destroyObjectOwnedNpcSlot' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/*.txt
```

Then read the generated body: `clearPendingChildNpc` at
`0x800EC698` on `MEM_W[a0+0]`, then `unlinkAndFreeChildNpcNode`
at `0x800EC6A4`. Classify against the companion name; do not
invent a name.

Expected splits:

- H1: all four sources already `clearPendingAndDestroyChildNpc` at
  size `0x3C`. Confirm.
- H2: rename the stale `func_800EC684` placeholder(s) to
  `clearPendingAndDestroyChildNpc` (TOML and/or generated
  headers/body/INL and/or jal sites).
- H3: document the leftover/collision/size miss; leave the name.
- H4: fill the missing source or leave as `func_*`.

Do not reopen the s1744 six-entry, s1760 jump-table, s1776
main-text, s1792 unwatched-caller, or s1808 jal/`prev_pc` Rice
recipes. The next 15-title REVISIT is the M4 accumulator
boundary, not another `submitGfxFrame` PC set.
