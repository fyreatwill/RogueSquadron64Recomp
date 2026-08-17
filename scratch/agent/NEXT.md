# NEXT work unit (s1794)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the leftover-`func_800E7390` census. Last-15 ledger titles after
s1793 include the s1792 revisit (`selected H3 unwatched submitGfx
callers`), so the 15-title all-sweep REVISIT gate does not fire.

Census leftover `func_800E7390` / companion
`tickFighterSquadronWithSplinePaths` (`0x800E7390`, size `0x4D0`).
Neighbor peek already: TOML still says `func_800E7390`; generated
headers/body, overlay INL, and `mission_overlay.txt` already use the
human name.

Competing hypotheses:

- H1: already synchronized — TOML, generated headers/body, overlay INL,
  and companion all agree on one name (confirm only; no rename).
- H2: TOML still `func_800E7390` while generated headers/body and
  section-4 already use `tickFighterSquadronWithSplinePaths`. Fix the
  stale placeholder.
- H3: leftover splat, overlay collision, or size/boundary disagreement
  (previous `transformCraftAnchorsApplySubFx3` ends at `0x800E7390`;
  next occupant must match `0x800E7390 + 0x4D0`). Do not invent a name.
- H4: companion, generated body, TOML, or section-4 row is missing.

Exact commands (no game run):

```
# TOML + generated + overlay INL
grep -n '800E7390\|tickFighterSquadronWithSplinePaths\|func_800E7390' \
  syms/rogue_squadron.syms.toml \
  ../N64Recomp/RecompiledFuncs/funcs.h \
  ../N64Recomp/RecompiledFuncs/recomp_overlays.inl
# generated body (funcs_39.c family)
grep -n 'func_800E7390\|tickFighterSquadronWithSplinePaths' \
  ../N64Recomp/RecompiledFuncs/funcs_3*.c
# companion overlays
grep -n '800E7390\|tickFighterSquadronWithSplinePaths\|func_800E7390' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/*.txt
```

Then read the generated body: first/last insn, previous
`transformCraftAnchorsApplySubFx3` / next occupant, jal targets, and
the section-4 `ovl_mission` row (base `0x800A5130`). Compare against
the companion comment (per-member spline paths + 3D audio + objective
counters + teardown).

Expected splits:

- H1: all four sources already `tickFighterSquadronWithSplinePaths` (or
  all already leftover `func_800E7390` with a documented reason). Confirm.
- H2: rename the stale TOML placeholder to the human name already used
  by generated/section-4.
- H3: document the leftover/collision/size miss; leave the name.
- H4: fill the missing source or leave as `func_*`.

Do not reopen the s1744 six-entry, s1760 jump-table, s1776 main-text,
or s1792 unwatched-caller Rice recipes. The next 15-title REVISIT
(after this sweep resumes) watches `submitGfxFrame` jal-sites / `$ra`,
not another function-entry PC set.
