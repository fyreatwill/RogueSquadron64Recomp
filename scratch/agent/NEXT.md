# NEXT work unit (s1814)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume leftover `func_800EC388`. Last-15 ledger titles after
s1813 still include the s1808 revisit (`selected H2 menuIn/mission
jal-sites`), so the 15-title all-sweep REVISIT gate does not fire.

Census leftover `func_800EC388` (`0x800EC388`, size `0x150`).
Neighbor peek already: companion `mission_overlay.txt` maps
`unlinkAndFreeChildNpcNode = 0x800EC388`; generated `funcs.h` /
`funcs_39.c` / overlay INL already say `unlinkAndFreeChildNpcNode`;
TOML still `{ name = "func_800EC388", vram = 0x800EC388, size = 0x150 }`.
Previous leftover is now `allocObjectPoolNode` (`0x800EC110`,
`0x278`; s1813 synchronized). First insn `addiu $sp, $sp, -0x18`;
last live `jr $ra` / `addiu $sp, $sp, 0x18` at `0x800EC4D0` /
`0x800EC4D4`. Sole generated `jal 0x800EC388` is inside
`clearPendingAndDestroyChildNpc` at `0x800EC6A4`. Next occupant
is `resetObjectContextPool` (`0x800EC4D8`, `0x3C`; generated
already named; TOML still `func_800EC4D8`).

Competing hypotheses:

- H1: already synchronized — TOML, generated headers/body, overlay
  INL, and companion already agree on `unlinkAndFreeChildNpcNode`
  with matching size (confirm only; no rename).
- H2: one or more sources still carry stale `func_800EC388`.
  Companion and generated already have `unlinkAndFreeChildNpcNode`.
  Rename the stale sources to that companion name (do not invent
  a name). If the live body does not match an unlink-and-free,
  leave the leftover and do not steal the name.
- H3: leftover splat, overlay collision, or size/boundary
  disagreement (previous `allocObjectPoolNode` ends at
  `0x800EC388`; generated next occupant is `resetObjectContextPool`
  at `0x800EC4D8`). Do not invent a name.
- H4: companion, generated body, TOML, or section-4 row is missing.

Exact commands (no game run):

```
# TOML + generated + overlay INL
grep -n '800EC388\|func_800EC388\|unlinkAndFreeChildNpcNode\|800EC4D8\|resetObjectContextPool' \
  syms/rogue_squadron.syms.toml \
  ../N64Recomp/RecompiledFuncs/funcs.h \
  ../N64Recomp/RecompiledFuncs/recomp_overlays.inl
# generated body + sole caller
grep -n 'func_800EC388\|unlinkAndFreeChildNpcNode\|jal         0x800EC388' \
  ../N64Recomp/RecompiledFuncs/funcs_3*.c \
  ../N64Recomp/RecompiledFuncs/funcs_4*.c
# companion overlays
grep -n '800EC388\|func_800EC388\|unlinkAndFreeChildNpcNode\|800EC4D8\|resetObjectContextPool' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/*.txt
```

Then read the generated body: node = `MEM_W[a0+0]`, extra =
`MEM_BU[a0+4]`, `(node_byte0 + extra) == 4` unlink from the
`-0x3F30`/`-0x3F2C` lists (`0x8010C0D0`/`0x8010C0D4`), then
`rs_free(node)`. Classify against the companion name; do not
invent a name.

Expected splits:

- H1: all four sources already `unlinkAndFreeChildNpcNode` at
  size `0x150`. Confirm.
- H2: rename the stale `func_800EC388` placeholder(s) to
  `unlinkAndFreeChildNpcNode` (TOML and/or generated
  headers/body/INL and/or the `clearPendingAndDestroyChildNpc`
  jal site).
- H3: document the leftover/collision/size miss; leave the name.
- H4: fill the missing source or leave as `func_*`.

Do not reopen the s1744 six-entry, s1760 jump-table, s1776
main-text, s1792 unwatched-caller, or s1808 jal/`prev_pc` Rice
recipes. The next 15-title REVISIT is the M4 accumulator
boundary, not another `submitGfxFrame` PC set.
