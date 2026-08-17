# NEXT work unit (s1809)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume `npcAtPtUpdate`. Last-15 ledger titles after s1808 include the
s1808 revisit (`selected H2 menuIn/mission jal-sites`), so the
15-title all-sweep REVISIT gate does not fire.

Census `npcAtPtUpdate` (`0x800EA5E0`). Neighbor peek already:
TOML, generated headers/body, overlay INL, and companion all use
`npcAtPtUpdate` (first insn `addiu $sp, $sp, -0xC8` at `0x800EA5E0`;
last live `jr $ra` / `addiu $sp, $sp, 0xC8` at `0x800EB97C`/`0x800EB980`;
section-4 `.offset = 0x000454B0`, `.rom_size = 0x000013A4`); companion
`mission_overlay.txt` names it with no comment. Previous
`npcAtPtPlaySkywalkerErrorCallout` now occupies `0x800EA470` size
`0x170` (s1807 renamed the TOML row). Next leftover `func_800EB984`
starts at `0x800EA5E0 + 0x13A4` (generated/companion already
`resetObjectPoolListHead`).

Competing hypotheses:

- H1: already synchronized — TOML, generated headers/body, overlay INL,
  and companion all agree on `npcAtPtUpdate` with matching size
  (confirm only; no rename).
- H2: one source still carries a stale `func_800EA5E0` placeholder.
  Fix the stale source (do not invent a name).
- H3: leftover splat, overlay collision, or size/boundary disagreement
  (previous `npcAtPtPlaySkywalkerErrorCallout` ends at `0x800EA5E0`;
  generated next occupant is `resetObjectPoolListHead` at `0x800EB984`).
  Do not invent a name.
- H4: companion, generated body, TOML, or section-4 row is missing.

Exact commands (no game run):

```
# TOML + generated + overlay INL
grep -n '800EA5E0\|func_800EA5E0\|npcAtPtUpdate\|800EB984\|resetObjectPoolListHead\|func_800EB984' \
  syms/rogue_squadron.syms.toml \
  ../N64Recomp/RecompiledFuncs/funcs.h \
  ../N64Recomp/RecompiledFuncs/recomp_overlays.inl
# generated body (funcs_39.c family)
grep -n 'npcAtPtUpdate\|func_800EA5E0\|resetObjectPoolListHead' \
  ../N64Recomp/RecompiledFuncs/funcs_3*.c
# companion overlays
grep -n '800EA5E0\|func_800EA5E0\|npcAtPtUpdate\|800EB984\|resetObjectPoolListHead\|func_800EB984' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/*.txt
```

Then read the generated body: first/last insn, previous
`npcAtPtPlaySkywalkerErrorCallout` / next `resetObjectPoolListHead`,
and the section-4 `ovl_mission` row (base `0x800A5130`). Classify the
`npcXxxUpdate` table if present; do not invent a name if the body
does not match the existing generated/companion name.

Expected splits:

- H1: all four sources already `npcAtPtUpdate` at size `0x13A4`. Confirm.
- H2: rename the stale `func_800EA5E0` placeholder to match the
  generated/companion human name.
- H3: document the leftover/collision/size miss; leave the name.
- H4: fill the missing source or leave as `func_*`.

Do not reopen the s1744 six-entry, s1760 jump-table, s1776 main-text,
s1792 unwatched-caller, or s1808 jal/`prev_pc` Rice recipes. The next
15-title REVISIT is the M4 accumulator boundary, not another
`submitGfxFrame` PC set.
