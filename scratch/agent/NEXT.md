# NEXT work unit (s1819)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume leftover `func_800EC6C0`. Last-15 ledger titles after
s1818 still include the s1808 revisit (`selected H2 menuIn/mission
jal-sites`), so the 15-title all-sweep REVISIT gate does not fire.

Census leftover `func_800EC6C0` (`0x800EC6C0`, size `0x2C`).
Neighbor peek already: companion `mission_overlay.txt` maps
`destroyObjectOwnedNpcSlot = 0x800EC6C0`; generated `funcs.h` /
`funcs_40.c` / overlay INL already say
`destroyObjectOwnedNpcSlot`; TOML still
`{ name = "func_800EC6C0", vram = 0x800EC6C0, size = 0x2C }`.
Previous leftover is now `clearPendingAndDestroyChildNpc`
(`0x800EC684`, `0x3C`; s1818 synchronized). First insn
`addiu $sp, $sp, -0x18`; last live `jr $ra` / `addiu $sp, $sp, 0x18`
at `0x800EC6E4` / `0x800EC6E8`. `lbu +0x1A4`; if nonzero `lhu +0x198`
then `jal destroyNpcSlotByIndex` (`0x8003ED74`) at `0x800EC6D8`.
Companion lists 22 callers; generated has 21 `jal 0x800EC6C0` sites
(17 in `funcs_36.c`–`funcs_39.c` plus 4 in `funcs_18.c`/`funcs_19.c`).
Next occupant is `fake_func_800EC6EC` (`0x800EC6EC`, `0x4`; already
named).

Competing hypotheses:

- H1: already synchronized — TOML, generated headers/body, overlay
  INL, and companion already agree on `destroyObjectOwnedNpcSlot`
  with matching size (confirm only; no rename).
- H2: one or more sources still carry stale `func_800EC6C0`.
  Companion and generated already have `destroyObjectOwnedNpcSlot`.
  Rename the stale sources to that companion name (do not invent
  a name). If the live body does not gate on `obj+0x1A4` and call
  `destroyNpcSlotByIndex(obj+0x198)`, leave the leftover and do not
  steal the name.
- H3: leftover splat, overlay collision, or size/boundary
  disagreement (previous `clearPendingAndDestroyChildNpc` ends at
  `0x800EC6C0`; generated next occupant is `fake_func_800EC6EC` at
  `0x800EC6EC`). Do not invent a name.
- H4: companion, generated body, TOML, or section-4 row is missing.

Exact commands (no game run):

```
# TOML + generated + overlay INL
grep -n '800EC6C0\|func_800EC6C0\|destroyObjectOwnedNpcSlot\|800EC6EC\|fake_func_800EC6EC' \
  syms/rogue_squadron.syms.toml \
  ../N64Recomp/RecompiledFuncs/funcs.h \
  ../N64Recomp/RecompiledFuncs/recomp_overlays.inl
# generated body + callers
grep -n 'func_800EC6C0\|destroyObjectOwnedNpcSlot\|jal         0x800EC6C0' \
  ../N64Recomp/RecompiledFuncs/funcs_1*.c \
  ../N64Recomp/RecompiledFuncs/funcs_3*.c \
  ../N64Recomp/RecompiledFuncs/funcs_4*.c
# companion overlays
grep -n '800EC6C0\|func_800EC6C0\|destroyObjectOwnedNpcSlot\|800EC6EC\|fake_func_800EC6EC' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/*.txt
```

Then read the generated body: `lbu +0x1A4` at `0x800EC6C8`; on
nonzero `lhu +0x198` then `destroyNpcSlotByIndex` at `0x800EC6D8`.
Classify against the companion name; do not invent a name.

Expected splits:

- H1: all four sources already `destroyObjectOwnedNpcSlot` at
  size `0x2C`. Confirm.
- H2: rename the stale `func_800EC6C0` placeholder(s) to
  `destroyObjectOwnedNpcSlot` (TOML and/or generated
  headers/body/INL and/or jal sites).
- H3: document the leftover/collision/size miss; leave the name.
- H4: fill the missing source or leave as `func_*`.

Do not reopen the s1744 six-entry, s1760 jump-table, s1776
main-text, s1792 unwatched-caller, or s1808 jal/`prev_pc` Rice
recipes. The next 15-title REVISIT is the M4 accumulator
boundary, not another `submitGfxFrame` PC set.
