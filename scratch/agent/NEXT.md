# NEXT work unit (s1806)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume `computeNpcOrientationFromAimVectors`. Last-15 ledger titles after
s1805 include the s1792 revisit (`selected H3 unwatched submitGfx
callers`), so the 15-title all-sweep REVISIT gate does not fire.

Census `computeNpcOrientationFromAimVectors` (`0x800E9EC4`). Neighbor peek
already: TOML still `func_800E9EC4` (`0x5AC`); generated headers/body
and overlay INL already `computeNpcOrientationFromAimVectors` (first insn
`addiu $sp, $sp, -0x1B0` at `0x800E9EC4`; last live `jr $ra` /
`addiu $sp, $sp, 0x1B0` at `0x800EA468`/`0x800EA46C`; section-4
`.offset = 0x00044D94`, `.rom_size = 0x000005AC`); companion
`mission_overlay.txt` names it (no comment). Next occupant
`npcAtPtPlaySkywalkerErrorCallout` starts at `0x800EA470`
(`0x800E9EC4 + 0x5AC`). Previous `spawnObjectImpactEffectWithSound` now
occupies `0x800E9D74` size `0x150` (s1805 renamed the TOML row).

Competing hypotheses:

- H1: already synchronized — TOML, generated headers/body, overlay INL,
  and companion all agree on `computeNpcOrientationFromAimVectors` with
  matching size (confirm only; no rename).
- H2: one source still carries a stale `func_800E9EC4` placeholder.
  Fix the stale source (do not invent a name).
- H3: leftover splat, overlay collision, or size/boundary disagreement
  (previous `spawnObjectImpactEffectWithSound` ends at `0x800E9EC4`;
  generated next occupant is `npcAtPtPlaySkywalkerErrorCallout` at
  `0x800EA470`). Do not invent a name.
- H4: companion, generated body, TOML, or section-4 row is missing.

Exact commands (no game run):

```
# TOML + generated + overlay INL
grep -n '800E9EC4\|func_800E9EC4\|computeNpcOrientationFromAimVectors\|800EA470\|npcAtPtPlaySkywalkerErrorCallout' \
  syms/rogue_squadron.syms.toml \
  ../N64Recomp/RecompiledFuncs/funcs.h \
  ../N64Recomp/RecompiledFuncs/recomp_overlays.inl
# generated body (funcs_39.c family)
grep -n 'computeNpcOrientationFromAimVectors\|func_800E9EC4\|npcAtPtPlaySkywalkerErrorCallout' \
  ../N64Recomp/RecompiledFuncs/funcs_3*.c
# companion overlays
grep -n '800E9EC4\|func_800E9EC4\|computeNpcOrientationFromAimVectors\|800EA470\|npcAtPtPlaySkywalkerErrorCallout' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/*.txt
```

Then read the generated body: first/last insn, previous
`spawnObjectImpactEffectWithSound` / next `npcAtPtPlaySkywalkerErrorCallout`,
and the section-4 `ovl_mission` row (base `0x800A5130`). Companion has
no comment — classify from the body; do not invent a name if the body
does not match the existing generated/companion name.

Expected splits:

- H1: all four sources already `computeNpcOrientationFromAimVectors` at
  size `0x5AC`. Confirm.
- H2: rename the stale `func_800E9EC4` placeholder to match the
  generated/companion human name.
- H3: document the leftover/collision/size miss; leave the name.
- H4: fill the missing source or leave as `func_*`.

Do not reopen the s1744 six-entry, s1760 jump-table, s1776 main-text,
or s1792 unwatched-caller Rice recipes. The next 15-title REVISIT
(after this sweep resumes) watches `submitGfxFrame` jal-sites / `$ra`,
not another function-entry PC set.
