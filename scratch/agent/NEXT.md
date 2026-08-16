# NEXT work unit (s1696)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the exact generated-symbol census. Last-15 titles after s1695
include the s1682 retail-entry revisit, so the 15-title REVISIT gate
does not fire. Do not start another retail-entry or M4 experiment.

Candidate: `playerAtStInit` at `0x800D1088` (size `0x1C0`). Companion,
generated headers, overlays.inl, and the project TOML already use
`playerAtStInit`. Previous is `npcAtStUpdate` at `0x800CFE7C`. Next
companion neighbor is `playerAtStUpdate` at `0x800D2208` (skips
helpers); next contiguous generated/TOML neighbor is
`spawnPlayerAtStCannonFire` / `func_800D1248` at `0x800D1248`.

Competing hypotheses and discriminator:

- H1: companion name, live generated body, exact
  `0x800CFE7C`/`0x800D1248` boundaries, TOML size, and section-4 overlay
  span already agree — confirm and leave (or only correct a stale TOML
  placeholder).
- H2: the generated symbol is still `func_800D1088` (or a wrong name)
  while companion/body/span agree — synchronize the name in TOML /
  generated headers via the usual census edits.
- H3: skip this address (fake fragment, overlay collision that is the
  real occupant, size/boundary disagreement, or no independent name).
- H4: the site is not evaluable this iteration (missing companion file,
  generated body, or TOML/section-4 row).

Discriminator: one static census, no game run.

```sh
# companion
grep -n 'playerAtStInit\|800D1088\|spawnPlayerAtStCannonFire\|800D1248\|playerAtStUpdate\|800D2208' \
  ~/Documents/Tools/rogue_squadron64/symbol_files/mission_overlay.txt \
  ~/Documents/Tools/rogue_squadron64/symbol_files/menu_overlay.txt
# generated + TOML + overlay table
grep -n 'playerAtStInit\|func_800D1088\|0x800D1088\|spawnPlayerAtStCannonFire\|func_800D1248\|0x800D1248' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl \
  syms/rogue_squadron.syms.toml
# body window in the owning funcs_*.c (expect funcs_37.c from s1695)
```

Expected splits:

- H1: all four sources already use `playerAtStInit` and size `0x1C0`;
  record confirmation; next candidate `func_800D1248` /
  `spawnPlayerAtStCannonFire`.
- H2: rename a stale placeholder where the generated/TOML copy is stale.
- H3: leave the current name and document why; pick the next contiguous
  mission function.
- H4: stop and write the missing artifact.

Do not expand into a second function in the same iteration.
