# NEXT work unit (s1813)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume leftover `func_800EC110`. Last-15 ledger titles after
s1812 still include the s1808 revisit (`selected H2 menuIn/mission
jal-sites`), so the 15-title all-sweep REVISIT gate does not fire.

Census leftover `func_800EC110` (`0x800EC110`, size `0x278`).
Neighbor peek already: companion `main_overlay.txt` maps
`allocObjectPoolNode = 0x800EC110`; mission leftover
`func_800EC110 = 0x800EC110`; TOML `{ name = "func_800EC110",
vram = 0x800EC110, size = 0x278 }`; generated `funcs.h` /
`funcs_39.c` / overlay INL still say `func_800EC110`. Previous
leftover `fake_func_800EC10C` occupies `0x800EC10C` size `0x4`
(s1812 confirmed). First insn `addiu $sp, $sp, -0x20`; last live
`jr $ra` / `addiu $sp, $sp, 0x20` at `0x800EC380` / `0x800EC384`.
Sole generated `jal 0x800EC110` is inside `createAndInitObject`
at `0x800EC5B4`. Next occupant is leftover `func_800EC388`
(`0x800EC388`, `0x150`; companion `unlinkAndFreeChildNpcNode`).

Competing hypotheses:

- H1: already synchronized — TOML, generated headers/body, overlay
  INL, and companion already agree on `allocObjectPoolNode` with
  matching size (confirm only; no rename).
- H2: one or more sources still carry stale `func_800EC110`.
  Companion `main_overlay.txt` already has `allocObjectPoolNode`.
  Rename the stale sources to that companion name (do not invent
  a name). If the live body does not match an object-pool
  allocator, leave the leftover and do not steal the name.
- H3: leftover splat, overlay collision, or size/boundary
  disagreement (previous leftover `fake_func_800EC10C` ends at
  `0x800EC110`; generated next occupant is leftover `func_800EC388`
  at `0x800EC388`). Do not invent a name.
- H4: companion, generated body, TOML, or section-4 row is missing.

Exact commands (no game run):

```
# TOML + generated + overlay INL
grep -n '800EC110\|func_800EC110\|allocObjectPoolNode\|800EC388\|func_800EC388\|unlinkAndFreeChildNpcNode' \
  syms/rogue_squadron.syms.toml \
  ../N64Recomp/RecompiledFuncs/funcs.h \
  ../N64Recomp/RecompiledFuncs/recomp_overlays.inl
# generated body + sole caller
grep -n 'func_800EC110\|allocObjectPoolNode\|jal         0x800EC110' \
  ../N64Recomp/RecompiledFuncs/funcs_3*.c \
  ../N64Recomp/RecompiledFuncs/funcs_4*.c
# companion overlays
grep -n '800EC110\|func_800EC110\|allocObjectPoolNode\|800EC388\|unlinkAndFreeChildNpcNode' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/*.txt
```

Then read the generated body: freelist load at `-0x3F30($s1)`
(`0x8010C0D0`), `rs_malloc(0x6C0)` empty-pool path, node init,
epilogue at `0x800EC380`/`0x800EC384`, and the
`createAndInitObject` jal at `0x800EC5B4`. Classify against the
companion allocator name; do not invent a name.

Expected splits:

- H1: all four sources already `allocObjectPoolNode` at size
  `0x278`. Confirm.
- H2: rename the stale `func_800EC110` placeholder(s) to
  `allocObjectPoolNode` (TOML and/or generated headers/body/INL
  and/or the `createAndInitObject` jal site).
- H3: document the leftover/collision/size miss; leave the name.
- H4: fill the missing source or leave as `func_*`.

Do not reopen the s1744 six-entry, s1760 jump-table, s1776
main-text, s1792 unwatched-caller, or s1808 jal/`prev_pc` Rice
recipes. The next 15-title REVISIT is the M4 accumulator
boundary, not another `submitGfxFrame` PC set.
