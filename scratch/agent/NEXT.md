# NEXT work unit (s1802)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the leftover `fake_func_800E9AD8` census. Last-15 ledger titles
after s1801 include the s1792 revisit (`selected H3 unwatched submitGfx
callers`), so the 15-title all-sweep REVISIT gate does not fire.

Census leftover `fake_func_800E9AD8` (`0x800E9AD8`, size `0x8`). Neighbor
peek already: TOML, generated headers/body, overlay INL, and companion
leftover already `fake_func_800E9AD8` (likely H1 confirm). Next leftover
after it is leftover `func_800E9AE0` (`0x800E9AE0`; neighbor peek: TOML
size `0x30` vs generated INL `0x114` — companion leftover notes
`func_800E9B10` is not real and splits this function; named
`playStateGatedDestroySound` sits at `0x800E9BF4`).

Competing hypotheses:

- H1: already synchronized — TOML, generated headers/body, overlay INL,
  and companion leftover all agree on `fake_func_800E9AD8` (confirm only;
  no rename).
- H2: one source still carries a stale `func_800E9AD8` placeholder.
  Fix the stale source.
- H3: leftover splat, overlay collision, or size/boundary disagreement
  (previous `initNpcHealthAndDetailFromChild` ends at `0x800E9AD8`; next
  occupant must match `0x800E9AD8 + 0x8` = `0x800E9AE0`). Do not invent
  a name. The two-insn body (`lw $v1, 0x34($v0)` / `addiu $v0, $zero, -1`)
  is an orphan only if the next prologue is a real function start (neighbor
  peek: `func_800E9AE0` is `addiu $sp, $sp, -0x40`).
- H4: companion, generated body, TOML, or section-4 row is missing.

Exact commands (no game run):

```
# TOML + generated + overlay INL
grep -n '800E9AD8\|fake_func_800E9AD8\|func_800E9AD8' \
  syms/rogue_squadron.syms.toml \
  ../N64Recomp/RecompiledFuncs/funcs.h \
  ../N64Recomp/RecompiledFuncs/recomp_overlays.inl
# generated body (funcs_39.c family)
grep -n 'fake_func_800E9AD8\|func_800E9AD8' \
  ../N64Recomp/RecompiledFuncs/funcs_3*.c
# companion overlays
grep -n '800E9AD8\|fake_func_800E9AD8\|func_800E9AD8' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/*.txt
```

Then read the generated body: first/last insn, previous
`initNpcHealthAndDetailFromChild` / next leftover `func_800E9AE0`,
and the section-4 `ovl_mission` row (base `0x800A5130`). Companion
leftover comment is only `segment:mission_overlay` — classify from
the body, do not invent a name.

Expected splits:

- H1: all four sources already `fake_func_800E9AD8`. Confirm.
- H2: rename the stale placeholder to the leftover name.
- H3: document the leftover/collision/size miss; leave the name.
- H4: fill the missing source or leave as `func_*`.

Do not reopen the s1744 six-entry, s1760 jump-table, s1776 main-text,
or s1792 unwatched-caller Rice recipes. The next 15-title REVISIT
(after this sweep resumes) watches `submitGfxFrame` jal-sites / `$ra`,
not another function-entry PC set.
