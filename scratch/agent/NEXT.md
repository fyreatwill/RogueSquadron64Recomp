# NEXT work unit (s1798)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the leftover `fake_func_800E8A34` census. Last-15 ledger titles
after s1797 include the s1792 revisit (`selected H3 unwatched submitGfx
callers`), so the 15-title all-sweep REVISIT gate does not fire.

Census leftover `fake_func_800E8A34` (`0x800E8A34`, size `0xC`).
Neighbor peek already: TOML, generated headers/body, overlay INL, and
`mission_overlay.txt` already use the leftover name (likely H1 confirm).
Next leftover after it is `func_800E8A40` / companion
`runDestructionPhaseSequence` (`0x800E8A40`, size `0x49C`; neighbor
peek: TOML still `func_800E8A40`; generated already the human name).

Competing hypotheses:

- H1: already synchronized — TOML, generated headers/body, overlay INL,
  and companion all agree on leftover `fake_func_800E8A34` (confirm only;
  no rename).
- H2: one source still carries a stale `func_800E8A34` placeholder.
  Fix the stale source.
- H3: leftover splat, overlay collision, or size/boundary disagreement
  (previous `applyCraftAnimDetailParamsB` ends at `0x800E8A34`; next
  occupant must match `0x800E8A34 + 0xC` = `0x800E8A40`). Do not invent
  a name.
- H4: companion, generated body, TOML, or section-4 row is missing.

Exact commands (no game run):

```
# TOML + generated + overlay INL
grep -n '800E8A34\|fake_func_800E8A34\|func_800E8A34' \
  syms/rogue_squadron.syms.toml \
  ../N64Recomp/RecompiledFuncs/funcs.h \
  ../N64Recomp/RecompiledFuncs/recomp_overlays.inl
# generated body (funcs_39.c family)
grep -n 'func_800E8A34\|fake_func_800E8A34' \
  ../N64Recomp/RecompiledFuncs/funcs_3*.c
# companion overlays
grep -n '800E8A34\|fake_func_800E8A34\|func_800E8A34' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/*.txt
```

Then read the generated body: first/last insn, previous
`applyCraftAnimDetailParamsB` / next `runDestructionPhaseSequence`,
and the section-4 `ovl_mission` row (base `0x800A5130`). Companion
comment is only "segment:mission_overlay" — classify from the body.
A 3-instruction `lw $a0, 0x18($fp)` / `addu $a2, $a0, $zero` /
`sll $a1, $a2, 1` orphan is the expected leftover splat.

Expected splits:

- H1: all four sources already `fake_func_800E8A34`. Confirm.
- H2: rename the stale placeholder to the leftover name.
- H3: document the leftover/collision/size miss; leave the name.
- H4: fill the missing source or leave as `func_*`.

Do not reopen the s1744 six-entry, s1760 jump-table, s1776 main-text,
or s1792 unwatched-caller Rice recipes. The next 15-title REVISIT
(after this sweep resumes) watches `submitGfxFrame` jal-sites / `$ra`,
not another function-entry PC set.
