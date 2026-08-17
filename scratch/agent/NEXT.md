# NEXT work unit (s1807)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume `npcAtPtPlaySkywalkerErrorCallout`. Last-15 ledger titles after
s1806 include the s1792 revisit (`selected H3 unwatched submitGfx
callers`), so the 15-title all-sweep REVISIT gate does not fire.

Census `npcAtPtPlaySkywalkerErrorCallout` (`0x800EA470`). Neighbor peek
already: TOML still `func_800EA470` (`0x170`); generated headers/body
and overlay INL already `npcAtPtPlaySkywalkerErrorCallout` (first insn
`addiu $sp, $sp, -0x18` at `0x800EA470`; last live `jr $ra` /
`addiu $sp, $sp, 0x18` at `0x800EA5D8`/`0x800EA5DC`; section-4
`.offset = 0x00045340`, `.rom_size = 0x00000170`); companion
`mission_overlay.txt` names it (comment: called 3× from `npcAtPtUpdate`,
voiceId `0xC4` = "Skywalker!  What are you doing?!!"). Next occupant
`npcAtPtUpdate` starts at `0x800EA5E0` (`0x800EA470 + 0x170`). Previous
`computeNpcOrientationFromAimVectors` now occupies `0x800E9EC4` size
`0x5AC` (s1806 renamed the TOML row).

Competing hypotheses:

- H1: already synchronized — TOML, generated headers/body, overlay INL,
  and companion all agree on `npcAtPtPlaySkywalkerErrorCallout` with
  matching size (confirm only; no rename).
- H2: one source still carries a stale `func_800EA470` placeholder.
  Fix the stale source (do not invent a name).
- H3: leftover splat, overlay collision, or size/boundary disagreement
  (previous `computeNpcOrientationFromAimVectors` ends at `0x800EA470`;
  generated next occupant is `npcAtPtUpdate` at `0x800EA5E0`). Do not
  invent a name.
- H4: companion, generated body, TOML, or section-4 row is missing.

Exact commands (no game run):

```
# TOML + generated + overlay INL
grep -n '800EA470\|func_800EA470\|npcAtPtPlaySkywalkerErrorCallout\|800EA5E0\|npcAtPtUpdate' \
  syms/rogue_squadron.syms.toml \
  ../N64Recomp/RecompiledFuncs/funcs.h \
  ../N64Recomp/RecompiledFuncs/recomp_overlays.inl
# generated body (funcs_39.c family)
grep -n 'npcAtPtPlaySkywalkerErrorCallout\|func_800EA470\|npcAtPtUpdate' \
  ../N64Recomp/RecompiledFuncs/funcs_3*.c
# companion overlays
grep -n '800EA470\|func_800EA470\|npcAtPtPlaySkywalkerErrorCallout\|800EA5E0\|npcAtPtUpdate' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/*.txt
```

Then read the generated body: first/last insn, previous
`computeNpcOrientationFromAimVectors` / next `npcAtPtUpdate`,
and the section-4 `ovl_mission` row (base `0x800A5130`). Companion
comment claims three `npcAtPtUpdate` call sites and voiceId `0xC4` —
classify from the body; do not invent a name if the body does not
match the existing generated/companion name.

Expected splits:

- H1: all four sources already `npcAtPtPlaySkywalkerErrorCallout` at
  size `0x170`. Confirm.
- H2: rename the stale `func_800EA470` placeholder to match the
  generated/companion human name.
- H3: document the leftover/collision/size miss; leave the name.
- H4: fill the missing source or leave as `func_*`.

Do not reopen the s1744 six-entry, s1760 jump-table, s1776 main-text,
or s1792 unwatched-caller Rice recipes. The next 15-title REVISIT
(after this sweep resumes) watches `submitGfxFrame` jal-sites / `$ra`,
not another function-entry PC set.
