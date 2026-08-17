# NEXT work unit (s1800)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the leftover `func_800E8EDC` / `tickCraftWithPhasedDestruction`
census. Last-15 ledger titles after s1799 include the s1792 revisit
(`selected H3 unwatched submitGfx callers`), so the 15-title all-sweep
REVISIT gate does not fire.

Census leftover `func_800E8EDC` / companion `tickCraftWithPhasedDestruction`
(`0x800E8EDC`, size `0xBA8`). Neighbor peek already: TOML still carries
`func_800E8EDC`; generated headers/body, overlay INL, and
`mission_overlay.txt` already use the human name (likely H2 TOML-only).
Next leftover after it is `func_800E9A84` / companion
`initNpcHealthAndDetailFromChild` (`0x800E9A84`, size `0x54`; neighbor
peek: TOML still `func_800E9A84`; generated already the human name).

Competing hypotheses:

- H1: already synchronized — TOML, generated headers/body, overlay INL,
  and companion all agree on `tickCraftWithPhasedDestruction` (confirm only;
  no rename).
- H2: one source still carries a stale `func_800E8EDC` placeholder.
  Fix the stale source (neighbor peek: TOML).
- H3: leftover splat, overlay collision, or size/boundary disagreement
  (previous `runDestructionPhaseSequence` ends at `0x800E8EDC`; next
  occupant must match `0x800E8EDC + 0xBA8` = `0x800E9A84`). Do not invent
  a name.
- H4: companion, generated body, TOML, or section-4 row is missing.

Exact commands (no game run):

```
# TOML + generated + overlay INL
grep -n '800E8EDC\|tickCraftWithPhasedDestruction\|func_800E8EDC' \
  syms/rogue_squadron.syms.toml \
  ../N64Recomp/RecompiledFuncs/funcs.h \
  ../N64Recomp/RecompiledFuncs/recomp_overlays.inl
# generated body (funcs_39.c family)
grep -n 'func_800E8EDC\|tickCraftWithPhasedDestruction' \
  ../N64Recomp/RecompiledFuncs/funcs_3*.c
# companion overlays
grep -n '800E8EDC\|tickCraftWithPhasedDestruction\|func_800E8EDC' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/*.txt
```

Then read the generated body: first/last insn, previous
`runDestructionPhaseSequence` / next `initNpcHealthAndDetailFromChild`,
jal targets, and the section-4 `ovl_mission` row (base `0x800A5130`).
Companion comment is "craft from DAT template, per-frame tick, phased
destruction, objective counters, teardown" — classify from the body, do
not take the comment as proof.

Expected splits:

- H1: all four sources already `tickCraftWithPhasedDestruction`. Confirm.
- H2: rename the stale placeholder to the human name.
- H3: document the leftover/collision/size miss; leave the name.
- H4: fill the missing source or leave as `func_*`.

Do not reopen the s1744 six-entry, s1760 jump-table, s1776 main-text,
or s1792 unwatched-caller Rice recipes. The next 15-title REVISIT
(after this sweep resumes) watches `submitGfxFrame` jal-sites / `$ra`,
not another function-entry PC set.
