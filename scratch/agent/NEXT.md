# NEXT work unit (s1795)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the `npcGroundTroopUpdate` census. Last-15 ledger titles after
s1794 include the s1792 revisit (`selected H3 unwatched submitGfx
callers`), so the 15-title all-sweep REVISIT gate does not fire.

Census `npcGroundTroopUpdate` (`0x800E7860`, size `0xFC8`). Neighbor
peek already: TOML, generated headers/body, overlay INL, and
`mission_overlay.txt` already use the human name. Next leftover after
it is `func_800E8828` / companion `playAttachmentCueNoTexture`.

Competing hypotheses:

- H1: already synchronized — TOML, generated headers/body, overlay INL,
  and companion all agree on `npcGroundTroopUpdate` (confirm only; no
  rename).
- H2: one source still carries a stale `func_800E7860` placeholder.
  Fix the stale source.
- H3: leftover splat, overlay collision, or size/boundary disagreement
  (previous `tickFighterSquadronWithSplinePaths` ends at `0x800E7860`;
  next occupant must match `0x800E7860 + 0xFC8` = `0x800E8828`). Do
  not invent a name.
- H4: companion, generated body, TOML, or section-4 row is missing.

Exact commands (no game run):

```
# TOML + generated + overlay INL
grep -n '800E7860\|npcGroundTroopUpdate\|func_800E7860' \
  syms/rogue_squadron.syms.toml \
  ../N64Recomp/RecompiledFuncs/funcs.h \
  ../N64Recomp/RecompiledFuncs/recomp_overlays.inl
# generated body (funcs_39.c family)
grep -n 'func_800E7860\|npcGroundTroopUpdate' \
  ../N64Recomp/RecompiledFuncs/funcs_3*.c
# companion overlays
grep -n '800E7860\|npcGroundTroopUpdate\|func_800E7860' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/*.txt
```

Then read the generated body: first/last insn, previous
`tickFighterSquadronWithSplinePaths` / next `playAttachmentCueNoTexture`,
jal targets, the two `jr $v0` tables (`0x800E78C4`, `0x800E80E8`), and
the section-4 `ovl_mission` row (base `0x800A5130`). Companion comment
is segment-only — classify the jump-table cases from the body.

Expected splits:

- H1: all four sources already `npcGroundTroopUpdate`. Confirm.
- H2: rename the stale placeholder to the human name.
- H3: document the leftover/collision/size miss; leave the name.
- H4: fill the missing source or leave as `func_*`.

Do not reopen the s1744 six-entry, s1760 jump-table, s1776 main-text,
or s1792 unwatched-caller Rice recipes. The next 15-title REVISIT
(after this sweep resumes) watches `submitGfxFrame` jal-sites / `$ra`,
not another function-entry PC set.
