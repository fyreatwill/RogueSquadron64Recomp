# NEXT work unit (s1816)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume leftover `func_800EC514`. Last-15 ledger titles after
s1815 still include the s1808 revisit (`selected H2 menuIn/mission
jal-sites`), so the 15-title all-sweep REVISIT gate does not fire.

Census leftover `func_800EC514` (`0x800EC514`, size `0x74`).
Neighbor peek already: companion `mission_overlay.txt` maps
`freeAllObjectContextPoolNodes = 0x800EC514`; generated `funcs.h` /
`funcs_40.c` / overlay INL already say `freeAllObjectContextPoolNodes`;
TOML still `{ name = "func_800EC514", vram = 0x800EC514, size = 0x74 }`.
Previous leftover is now `resetObjectContextPool` (`0x800EC4D8`,
`0x3C`; s1815 synchronized). First insn `lui $v1, 0x8011`; last live
`jr $ra` / `addiu $sp, $sp, 0x18` at `0x800EC580` / `0x800EC584`.
Walks list `0x8010C0D0` then `0x8010C0D4`, `rs_free` each via `+0xC`
next. Sole generated `jal 0x800EC514` is at `0x800FBAD4` in
`endMissionCleanup`. Next occupant is `createAndInitObject`
(`0x800EC588`, `0xFC`; generated already named; TOML still
`func_800EC588`).

Competing hypotheses:

- H1: already synchronized — TOML, generated headers/body, overlay
  INL, and companion already agree on `freeAllObjectContextPoolNodes`
  with matching size (confirm only; no rename).
- H2: one or more sources still carry stale `func_800EC514`.
  Companion and generated already have `freeAllObjectContextPoolNodes`.
  Rename the stale sources to that companion name (do not invent
  a name). If the live body does not match a walk-and-free of both
  context-pool lists, leave the leftover and do not steal the name.
- H3: leftover splat, overlay collision, or size/boundary
  disagreement (previous `resetObjectContextPool` ends at
  `0x800EC514`; generated next occupant is
  `createAndInitObject` at `0x800EC588`). Do not invent a name.
- H4: companion, generated body, TOML, or section-4 row is missing.

Exact commands (no game run):

```
# TOML + generated + overlay INL
grep -n '800EC514\|func_800EC514\|freeAllObjectContextPoolNodes\|800EC588\|createAndInitObject' \
  syms/rogue_squadron.syms.toml \
  ../N64Recomp/RecompiledFuncs/funcs.h \
  ../N64Recomp/RecompiledFuncs/recomp_overlays.inl
# generated body + sole caller
grep -n 'func_800EC514\|freeAllObjectContextPoolNodes\|jal         0x800EC514' \
  ../N64Recomp/RecompiledFuncs/funcs_3*.c \
  ../N64Recomp/RecompiledFuncs/funcs_4*.c
# companion overlays
grep -n '800EC514\|func_800EC514\|freeAllObjectContextPoolNodes\|800EC588\|createAndInitObject' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/*.txt
```

Then read the generated body: walk `0x8010C0D0` then `0x8010C0D4`,
`rs_free` each via `+0xC` next. Classify against the companion
name; do not invent a name.

Expected splits:

- H1: all four sources already `freeAllObjectContextPoolNodes` at
  size `0x74`. Confirm.
- H2: rename the stale `func_800EC514` placeholder(s) to
  `freeAllObjectContextPoolNodes` (TOML and/or generated
  headers/body/INL and/or the `0x800FBAD4` jal site).
- H3: document the leftover/collision/size miss; leave the name.
- H4: fill the missing source or leave as `func_*`.

Do not reopen the s1744 six-entry, s1760 jump-table, s1776
main-text, s1792 unwatched-caller, or s1808 jal/`prev_pc` Rice
recipes. The next 15-title REVISIT is the M4 accumulator
boundary, not another `submitGfxFrame` PC set.
