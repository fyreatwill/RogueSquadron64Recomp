# NEXT work unit (s1804)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume `playStateGatedDestroySound`. Last-15 ledger titles after s1803
include the s1792 revisit (`selected H3 unwatched submitGfx callers`),
so the 15-title all-sweep REVISIT gate does not fire.

Census `playStateGatedDestroySound` (`0x800E9BF4`). Neighbor peek
already: TOML still `func_800E9BF4` (`0x180`); generated headers/body
and overlay INL already `playStateGatedDestroySound` (first insn
`addiu $sp, $sp, -0x38` at `0x800E9BF4`; section-4
`.offset = 0x00044AC4`, `.rom_size = 0x00000180`); companion
`mission_overlay.txt` names it ("selects a destruction sound by
object state and plays it (3D)"). Next occupant
`spawnObjectImpactEffectWithSound` starts at `0x800E9D74`
(`0x800E9BF4 + 0x180`). Previous leftover `func_800E9AE0` now
occupies `0x800E9AE0` size `0x114` (s1803 merged the TOML split).

Competing hypotheses:

- H1: already synchronized — TOML, generated headers/body, overlay INL,
  and companion all agree on `playStateGatedDestroySound` with matching
  size (confirm only; no rename).
- H2: one source still carries a stale `func_800E9BF4` placeholder.
  Fix the stale source (do not invent a name).
- H3: leftover splat, overlay collision, or size/boundary disagreement
  (previous leftover `func_800E9AE0` ends at `0x800E9BF4`; generated
  next occupant is `spawnObjectImpactEffectWithSound` at `0x800E9D74`).
  Do not invent a name.
- H4: companion, generated body, TOML, or section-4 row is missing.

Exact commands (no game run):

```
# TOML + generated + overlay INL
grep -n '800E9BF4\|func_800E9BF4\|playStateGatedDestroySound\|800E9D74\|spawnObjectImpactEffectWithSound' \
  syms/rogue_squadron.syms.toml \
  ../N64Recomp/RecompiledFuncs/funcs.h \
  ../N64Recomp/RecompiledFuncs/recomp_overlays.inl
# generated body (funcs_39.c family)
grep -n 'playStateGatedDestroySound\|func_800E9BF4\|spawnObjectImpactEffectWithSound' \
  ../N64Recomp/RecompiledFuncs/funcs_3*.c
# companion overlays
grep -n '800E9BF4\|func_800E9BF4\|playStateGatedDestroySound\|800E9D74\|spawnObjectImpactEffectWithSound' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/*.txt
```

Then read the generated body: first/last insn, previous leftover
`func_800E9AE0` / next `spawnObjectImpactEffectWithSound`, and the
section-4 `ovl_mission` row (base `0x800A5130`). Companion comment
claims a state-gated 3D destruction sound — classify from the body.

Expected splits:

- H1: all four sources already `playStateGatedDestroySound` at size
  `0x180`. Confirm.
- H2: rename the stale `func_800E9BF4` placeholder to match the
  generated/companion human name.
- H3: document the leftover/collision/size miss; leave the name.
- H4: fill the missing source or leave as `func_*`.

Do not reopen the s1744 six-entry, s1760 jump-table, s1776 main-text,
or s1792 unwatched-caller Rice recipes. The next 15-title REVISIT
(after this sweep resumes) watches `submitGfxFrame` jal-sites / `$ra`,
not another function-entry PC set.
