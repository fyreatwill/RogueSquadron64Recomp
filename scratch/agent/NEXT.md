# NEXT work unit (s1812)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume leftover `fake_func_800EC10C`. Last-15 ledger titles after
s1811 still include the s1808 revisit (`selected H2 menuIn/mission
jal-sites`), so the 15-title all-sweep REVISIT gate does not fire.

Census leftover `fake_func_800EC10C` (`0x800EC10C`, size `0x4`).
Neighbor peek already: TOML `{ name = "fake_func_800EC10C", vram =
0x800EC10C, size = 0x4 }`; generated `funcs.h` / `funcs_39.c` /
overlay INL and companion `mission_overlay.txt` already use
`fake_func_800EC10C` (single INVALID COP2 word `0x4A652950` /
`do_break` at `0x800EC10C`). Previous `npcPowerUpUpdate` occupies
`0x800EB990` size `0x77C` (s1811 confirmed). Next occupant is leftover
`func_800EC110` (`0x800EC110`, `0x278`; first insn `addiu $sp, $sp,
-0x20`; last live `jr $ra` / `addiu $sp, $sp, 0x20` at `0x800EC380`
/`0x800EC384`). Companion `main_overlay.txt` already maps
`allocObjectPoolNode = 0x800EC110`; mission leftover and generated
body still say `func_800EC110`.

Competing hypotheses:

- H1: already synchronized — TOML, generated headers/body, overlay INL,
  and companion leftover all agree on `fake_func_800EC10C` with matching
  size (confirm only; no rename).
- H2: one source still carries a stale `func_800EC10C` placeholder.
  Fix the stale source (do not invent a name).
- H3: leftover splat, overlay collision, or size/boundary disagreement
  (previous `npcPowerUpUpdate` ends at `0x800EC10C`; generated next
  occupant is leftover `func_800EC110` at `0x800EC110`). Do not invent
  a name.
- H4: companion, generated body, TOML, or section-4 row is missing.

Exact commands (no game run):

```
# TOML + generated + overlay INL
grep -n '800EC10C\|fake_func_800EC10C\|func_800EC10C\|800EC110\|func_800EC110\|allocObjectPoolNode' \
  syms/rogue_squadron.syms.toml \
  ../N64Recomp/RecompiledFuncs/funcs.h \
  ../N64Recomp/RecompiledFuncs/recomp_overlays.inl
# generated body
grep -n 'fake_func_800EC10C\|func_800EC10C\|func_800EC110\|allocObjectPoolNode' \
  ../N64Recomp/RecompiledFuncs/funcs_3*.c \
  ../N64Recomp/RecompiledFuncs/funcs_4*.c
# companion overlays
grep -n '800EC10C\|fake_func_800EC10C\|func_800EC10C\|800EC110\|func_800EC110\|allocObjectPoolNode' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/*.txt
```

Then read the generated body: the INVALID COP2 word, previous
`npcPowerUpUpdate` / next leftover `func_800EC110`, any
`jal 0x800EC10C` sites, and the section-4 `ovl_mission` row (base
`0x800A5130`). Classify as a leftover splat; do not invent a name.

Expected splits:

- H1: all four sources already `fake_func_800EC10C` at size `0x4`.
  Confirm.
- H2: rename the stale `func_800EC10C` placeholder to match the
  generated/companion leftover name.
- H3: document the leftover/collision/size miss; leave the name.
- H4: fill the missing source or leave as `func_*`.

Do not reopen the s1744 six-entry, s1760 jump-table, s1776 main-text,
s1792 unwatched-caller, or s1808 jal/`prev_pc` Rice recipes. The next
15-title REVISIT is the M4 accumulator boundary, not another
`submitGfxFrame` PC set.
