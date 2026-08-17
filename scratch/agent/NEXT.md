# NEXT work unit (s1817)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume leftover `func_800EC588`. Last-15 ledger titles after
s1816 still include the s1808 revisit (`selected H2 menuIn/mission
jal-sites`), so the 15-title all-sweep REVISIT gate does not fire.

Census leftover `func_800EC588` (`0x800EC588`, size `0xFC`).
Neighbor peek already: companion `mission_overlay.txt` maps
`createAndInitObject = 0x800EC588`; generated `funcs.h` /
`funcs_40.c` / overlay INL already say `createAndInitObject`;
TOML still `{ name = "func_800EC588", vram = 0x800EC588, size = 0xFC }`.
Previous leftover is now `freeAllObjectContextPoolNodes`
(`0x800EC514`, `0x74`; s1816 synchronized). First insn
`addiu $sp, $sp, -0x28`; last live `jr $ra` / `addiu $sp, $sp, 0x28`
at `0x800EC67C` / `0x800EC680`. `jal allocObjectPoolNode` at
`0x800EC5B4` with `a1+0x1AC`. Companion lists 21 callers
`(out_ptr_storage, spawn_data, template, extras_struct_or_null,
callback_or_null)` returning 1/3; generated has 16 call sites in
`funcs_36.c`–`funcs_39.c`. Next occupant is
`clearPendingAndDestroyChildNpc` (`0x800EC684`, `0x3C`; generated
already named; TOML still `func_800EC684`).

Competing hypotheses:

- H1: already synchronized — TOML, generated headers/body, overlay
  INL, and companion already agree on `createAndInitObject`
  with matching size (confirm only; no rename).
- H2: one or more sources still carry stale `func_800EC588`.
  Companion and generated already have `createAndInitObject`.
  Rename the stale sources to that companion name (do not invent
  a name). If the live body does not allocate via
  `allocObjectPoolNode` and init the object, leave the leftover
  and do not steal the name.
- H3: leftover splat, overlay collision, or size/boundary
  disagreement (previous `freeAllObjectContextPoolNodes` ends at
  `0x800EC588`; generated next occupant is
  `clearPendingAndDestroyChildNpc` at `0x800EC684`). Do not invent
  a name.
- H4: companion, generated body, TOML, or section-4 row is missing.

Exact commands (no game run):

```
# TOML + generated + overlay INL
grep -n '800EC588\|func_800EC588\|createAndInitObject\|800EC684\|clearPendingAndDestroyChildNpc' \
  syms/rogue_squadron.syms.toml \
  ../N64Recomp/RecompiledFuncs/funcs.h \
  ../N64Recomp/RecompiledFuncs/recomp_overlays.inl
# generated body + callers
grep -n 'func_800EC588\|createAndInitObject\|jal         0x800EC588' \
  ../N64Recomp/RecompiledFuncs/funcs_3*.c \
  ../N64Recomp/RecompiledFuncs/funcs_4*.c
# companion overlays
grep -n '800EC588\|func_800EC588\|createAndInitObject\|800EC684\|clearPendingAndDestroyChildNpc' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/*.txt
```

Then read the generated body: `allocObjectPoolNode` at
`0x800EC5B4` with `a1+0x1AC`, then init. Classify against the
companion name; do not invent a name.

Expected splits:

- H1: all four sources already `createAndInitObject` at
  size `0xFC`. Confirm.
- H2: rename the stale `func_800EC588` placeholder(s) to
  `createAndInitObject` (TOML and/or generated
  headers/body/INL and/or jal sites).
- H3: document the leftover/collision/size miss; leave the name.
- H4: fill the missing source or leave as `func_*`.

Do not reopen the s1744 six-entry, s1760 jump-table, s1776
main-text, s1792 unwatched-caller, or s1808 jal/`prev_pc` Rice
recipes. The next 15-title REVISIT is the M4 accumulator
boundary, not another `submitGfxFrame` PC set.
