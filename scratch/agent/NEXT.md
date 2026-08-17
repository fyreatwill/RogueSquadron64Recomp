# NEXT work unit (s1815)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume leftover `func_800EC4D8`. Last-15 ledger titles after
s1814 still include the s1808 revisit (`selected H2 menuIn/mission
jal-sites`), so the 15-title all-sweep REVISIT gate does not fire.

Census leftover `func_800EC4D8` (`0x800EC4D8`, size `0x3C`).
Neighbor peek already: companion `mission_overlay.txt` maps
`resetObjectContextPool = 0x800EC4D8`; generated `funcs.h` /
`funcs_40.c` / overlay INL already say `resetObjectContextPool`;
TOML still `{ name = "func_800EC4D8", vram = 0x800EC4D8, size = 0x3C }`.
Previous leftover is now `unlinkAndFreeChildNpcNode` (`0x800EC388`,
`0x150`; s1814 synchronized). First insn `addiu $sp, $sp, -0x18`;
last live `jr $ra` / `addiu $sp, $sp, 0x18` at `0x800EC50C` /
`0x800EC510`. Zeros `0x8010C0D0`/`0x8010C0D4`, then
`resetCraftSubsystemGlobal`, `resetObjectPoolListHead`,
`clearObjectPoolStateFlag`. Sole generated `jal 0x800EC4D8` is at
`0x800FA2D4` in `funcs_42.c`. Next occupant is
`freeAllObjectContextPoolNodes` (`0x800EC514`, `0x74`; generated
already named; TOML still `func_800EC514`).

Competing hypotheses:

- H1: already synchronized — TOML, generated headers/body, overlay
  INL, and companion already agree on `resetObjectContextPool`
  with matching size (confirm only; no rename).
- H2: one or more sources still carry stale `func_800EC4D8`.
  Companion and generated already have `resetObjectContextPool`.
  Rename the stale sources to that companion name (do not invent
  a name). If the live body does not match a context-pool reset,
  leave the leftover and do not steal the name.
- H3: leftover splat, overlay collision, or size/boundary
  disagreement (previous `unlinkAndFreeChildNpcNode` ends at
  `0x800EC4D8`; generated next occupant is
  `freeAllObjectContextPoolNodes` at `0x800EC514`). Do not invent
  a name.
- H4: companion, generated body, TOML, or section-4 row is missing.

Exact commands (no game run):

```
# TOML + generated + overlay INL
grep -n '800EC4D8\|func_800EC4D8\|resetObjectContextPool\|800EC514\|freeAllObjectContextPoolNodes' \
  syms/rogue_squadron.syms.toml \
  ../N64Recomp/RecompiledFuncs/funcs.h \
  ../N64Recomp/RecompiledFuncs/recomp_overlays.inl
# generated body + sole caller
grep -n 'func_800EC4D8\|resetObjectContextPool\|jal         0x800EC4D8' \
  ../N64Recomp/RecompiledFuncs/funcs_3*.c \
  ../N64Recomp/RecompiledFuncs/funcs_4*.c
# companion overlays
grep -n '800EC4D8\|func_800EC4D8\|resetObjectContextPool\|800EC514\|freeAllObjectContextPoolNodes' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/*.txt
```

Then read the generated body: zero `0x8010C0D0`/`0x8010C0D4`,
then `resetCraftSubsystemGlobal` / `resetObjectPoolListHead` /
`clearObjectPoolStateFlag`. Classify against the companion name;
do not invent a name.

Expected splits:

- H1: all four sources already `resetObjectContextPool` at
  size `0x3C`. Confirm.
- H2: rename the stale `func_800EC4D8` placeholder(s) to
  `resetObjectContextPool` (TOML and/or generated
  headers/body/INL and/or the `0x800FA2D4` jal site).
- H3: document the leftover/collision/size miss; leave the name.
- H4: fill the missing source or leave as `func_*`.

Do not reopen the s1744 six-entry, s1760 jump-table, s1776
main-text, s1792 unwatched-caller, or s1808 jal/`prev_pc` Rice
recipes. The next 15-title REVISIT is the M4 accumulator
boundary, not another `submitGfxFrame` PC set.
