# NEXT work unit (s1805)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume `spawnObjectImpactEffectWithSound`. Last-15 ledger titles after
s1804 include the s1792 revisit (`selected H3 unwatched submitGfx
callers`), so the 15-title all-sweep REVISIT gate does not fire.

Census `spawnObjectImpactEffectWithSound` (`0x800E9D74`). Neighbor peek
already: TOML still `func_800E9D74` (`0x150`); generated headers/body
and overlay INL already `spawnObjectImpactEffectWithSound` (first insn
`addiu $sp, $sp, -0x88` at `0x800E9D74`; section-4
`.offset = 0x00044C44`, `.rom_size = 0x00000150`); companion
`mission_overlay.txt` names it (no comment). Next occupant
`computeNpcOrientationFromAimVectors` starts at `0x800E9EC4`
(`0x800E9D74 + 0x150`). Previous `playStateGatedDestroySound` now
occupies `0x800E9BF4` size `0x180` (s1804 renamed the TOML row).

Competing hypotheses:

- H1: already synchronized — TOML, generated headers/body, overlay INL,
  and companion all agree on `spawnObjectImpactEffectWithSound` with
  matching size (confirm only; no rename).
- H2: one source still carries a stale `func_800E9D74` placeholder.
  Fix the stale source (do not invent a name).
- H3: leftover splat, overlay collision, or size/boundary disagreement
  (previous `playStateGatedDestroySound` ends at `0x800E9D74`; generated
  next occupant is `computeNpcOrientationFromAimVectors` at `0x800E9EC4`).
  Do not invent a name.
- H4: companion, generated body, TOML, or section-4 row is missing.

Exact commands (no game run):

```
# TOML + generated + overlay INL
grep -n '800E9D74\|func_800E9D74\|spawnObjectImpactEffectWithSound\|800E9EC4\|computeNpcOrientationFromAimVectors' \
  syms/rogue_squadron.syms.toml \
  ../N64Recomp/RecompiledFuncs/funcs.h \
  ../N64Recomp/RecompiledFuncs/recomp_overlays.inl
# generated body (funcs_39.c family)
grep -n 'spawnObjectImpactEffectWithSound\|func_800E9D74\|computeNpcOrientationFromAimVectors' \
  ../N64Recomp/RecompiledFuncs/funcs_3*.c
# companion overlays
grep -n '800E9D74\|func_800E9D74\|spawnObjectImpactEffectWithSound\|800E9EC4\|computeNpcOrientationFromAimVectors' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/*.txt
```

Then read the generated body: first/last insn, previous
`playStateGatedDestroySound` / next `computeNpcOrientationFromAimVectors`,
and the section-4 `ovl_mission` row (base `0x800A5130`). Companion has
no comment — classify from the body; do not invent a name if the body
does not match the existing generated/companion name.

Expected splits:

- H1: all four sources already `spawnObjectImpactEffectWithSound` at
  size `0x150`. Confirm.
- H2: rename the stale `func_800E9D74` placeholder to match the
  generated/companion human name.
- H3: document the leftover/collision/size miss; leave the name.
- H4: fill the missing source or leave as `func_*`.

Do not reopen the s1744 six-entry, s1760 jump-table, s1776 main-text,
or s1792 unwatched-caller Rice recipes. The next 15-title REVISIT
(after this sweep resumes) watches `submitGfxFrame` jal-sites / `$ra`,
not another function-entry PC set.
