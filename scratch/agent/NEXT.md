# NEXT work unit (s1803)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume leftover `func_800E9AE0`. Last-15 ledger titles after s1802
include the s1792 revisit (`selected H3 unwatched submitGfx callers`),
so the 15-title all-sweep REVISIT gate does not fire.

Census leftover `func_800E9AE0` (`0x800E9AE0`). Neighbor peek already:
TOML size `0x30` plus a following `func_800E9B10` (`0xE4`); generated
headers/body and overlay INL treat this as one `0x114` function (first
insn `addiu $sp, $sp, -0x40` at `0x800E9AE0`; last live `jr $ra` at
`0x800E9BEC` with delay `addiu $sp, $sp, 0x40` at `0x800E9BF0`); next
occupant `playStateGatedDestroySound` starts at `0x800E9BF4`. Companion
leftover is `func_800E9AE0`; the `fake_func_800B58B4` comment notes
`func_800E9B10` is not real and splits this function.
`ignored_symbols.txt` has `func_800E9B10` `ignore:true`.
`main_overlay.txt` names `initObjectAnimAndDetail = 0x800E9B10` (a
different overlay, not this occupant). `0x800E9B10` in the generated
body is mid-function `lui $at, 0x800B`, not a prologue.

Competing hypotheses:

- H1: already synchronized — TOML, generated headers/body, overlay INL,
  and companion leftover all agree on `func_800E9AE0` with matching size
  (confirm only; no rename). Unlikely given the `0x30` vs `0x114` split.
- H2: one source still carries a stale `func_800E9AE0` / `func_800E9B10`
  placeholder or the TOML size still splits a single generated function.
  Fix the stale source (do not invent a name).
- H3: leftover splat, overlay collision, or size/boundary disagreement
  (previous leftover `fake_func_800E9AD8` ends at `0x800E9AE0`; generated
  next occupant is `playStateGatedDestroySound` at `0x800E9BF4` =
  `0x800E9AE0 + 0x114`). Do not invent a name. Classify the
  `func_800E9B10` split from the body; the mid-function `lui` is not a
  function start.
- H4: companion, generated body, TOML, or section-4 row is missing.

Exact commands (no game run):

```
# TOML + generated + overlay INL
grep -n '800E9AE0\|func_800E9AE0\|800E9B10\|func_800E9B10\|800E9BF4\|playStateGatedDestroySound' \
  syms/rogue_squadron.syms.toml \
  ../N64Recomp/RecompiledFuncs/funcs.h \
  ../N64Recomp/RecompiledFuncs/recomp_overlays.inl
# generated body (funcs_39.c family)
grep -n 'func_800E9AE0\|func_800E9B10\|playStateGatedDestroySound' \
  ../N64Recomp/RecompiledFuncs/funcs_3*.c
# companion overlays + ignore list
grep -n '800E9AE0\|func_800E9AE0\|800E9B10\|func_800E9B10\|800E9BF4\|playStateGatedDestroySound\|initObjectAnimAndDetail' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/*.txt
```

Then read the generated body: first/last insn, mid-function `0x800E9B10`,
previous leftover `fake_func_800E9AD8` / next `playStateGatedDestroySound`,
and the section-4 `ovl_mission` row (base `0x800A5130`). Companion leftover
comment is only `segment:mission_overlay` plus the `fake_func_800B58B4`
split note — classify from the body, do not invent a name.

Expected splits:

- H1: all four sources already `func_800E9AE0` at size `0x114`. Confirm.
- H2: rename or resize the stale placeholder/split to match the generated
  single `0x114` leftover (keep `func_800E9AE0`; do not invent a name).
- H3: document the leftover/collision/size miss; leave the name.
- H4: fill the missing source or leave as `func_*`.

Do not reopen the s1744 six-entry, s1760 jump-table, s1776 main-text,
or s1792 unwatched-caller Rice recipes. The next 15-title REVISIT
(after this sweep resumes) watches `submitGfxFrame` jal-sites / `$ra`,
not another function-entry PC set.
