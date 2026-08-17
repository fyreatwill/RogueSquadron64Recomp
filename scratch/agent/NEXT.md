# NEXT work unit (s1811)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume `npcPowerUpUpdate`. Last-15 ledger titles after s1810 still
include the s1808 revisit (`selected H2 menuIn/mission jal-sites`), so
the 15-title all-sweep REVISIT gate does not fire.

Census `npcPowerUpUpdate` (`0x800EB990`). Neighbor peek already:
TOML `{ name = "npcPowerUpUpdate", vram = 0x800EB990, size = 0x77C }`;
generated `funcs.h` / `funcs_39.c` / overlay INL and companion
`mission_overlay.txt` already use `npcPowerUpUpdate` (first insn
`addiu $sp, $sp, -0x68` at `0x800EB990`; last live `jr $ra` /
`addiu $sp, $sp, 0x68` at `0x800EC104`/`0x800EC108`; section-4
`.offset = 0x00046860`, `.rom_size = 0x0000077C`). Previous
`resetObjectPoolListHead` occupies `0x800EB984` size `0xC` (s1810
synchronized). Next occupant is leftover `fake_func_800EC10C`
(`0x800EC10C`, `0x4`, INVALID COP2 word), then leftover
`func_800EC110` (companion `main_overlay.txt` already maps
`allocObjectPoolNode = 0x800EC110`; mission leftover and generated
body still say `func_800EC110`).

Competing hypotheses:

- H1: already synchronized — TOML, generated headers/body, overlay INL,
  and companion all agree on `npcPowerUpUpdate` with matching size
  (confirm only; no rename).
- H2: one source still carries a stale `func_800EB990` placeholder.
  Fix the stale source (do not invent a name).
- H3: leftover splat, overlay collision, or size/boundary disagreement
  (previous `resetObjectPoolListHead` ends at `0x800EB990`; generated
  next occupant is `fake_func_800EC10C` at `0x800EC10C`). Do not invent
  a name.
- H4: companion, generated body, TOML, or section-4 row is missing.

Exact commands (no game run):

```
# TOML + generated + overlay INL
grep -n '800EB990\|func_800EB990\|npcPowerUpUpdate\|800EC10C\|fake_func_800EC10C' \
  syms/rogue_squadron.syms.toml \
  ../N64Recomp/RecompiledFuncs/funcs.h \
  ../N64Recomp/RecompiledFuncs/recomp_overlays.inl
# generated body
grep -n 'npcPowerUpUpdate\|func_800EB990\|fake_func_800EC10C' \
  ../N64Recomp/RecompiledFuncs/funcs_3*.c \
  ../N64Recomp/RecompiledFuncs/funcs_4*.c
# companion overlays
grep -n '800EB990\|func_800EB990\|npcPowerUpUpdate\|800EC10C\|fake_func_800EC10C' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/*.txt
```

Then read the generated body: first/last insn, previous
`resetObjectPoolListHead` / next `fake_func_800EC10C`, any
`jal 0x800EB990` sites, the 9-way `npcXxxUpdate` table if present,
and the section-4 `ovl_mission` row (base `0x800A5130`). Classify
the body as a power-up NPC update; do not invent a name if the body
does not match the existing generated/companion name.

Expected splits:

- H1: all four sources already `npcPowerUpUpdate` at size `0x77C`.
  Confirm.
- H2: rename the stale `func_800EB990` placeholder to match the
  generated/companion human name.
- H3: document the leftover/collision/size miss; leave the name.
- H4: fill the missing source or leave as `func_*`.

Do not reopen the s1744 six-entry, s1760 jump-table, s1776 main-text,
s1792 unwatched-caller, or s1808 jal/`prev_pc` Rice recipes. The next
15-title REVISIT is the M4 accumulator boundary, not another
`submitGfxFrame` PC set.
