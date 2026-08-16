# NEXT work unit (s1697)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the exact generated-symbol census. Last-15 titles after s1696
include the s1682 retail-entry revisit, so the 15-title REVISIT gate
does not fire. Do not start another retail-entry or M4 experiment.

Candidate: `spawnPlayerAtStCannonFire` at `0x800D1248` (size `0x330`).
Companion, generated headers, and overlays.inl already use
`spawnPlayerAtStCannonFire`. TOML still has placeholder `func_800D1248`.
Previous is `playerAtStInit` at `0x800D1088`. Next companion /
generated neighbor is `advancePlayerAtStLocomotion` at `0x800D1578`
(TOML still `func_800D1578`).

Competing hypotheses and discriminator:

- H1: companion name, live generated body, exact
  `0x800D1088`/`0x800D1578` boundaries, TOML size, and section-4 overlay
  span already agree — confirm and leave (or only correct a stale TOML
  placeholder).
- H2: the generated symbol is still `func_800D1248` (or a wrong name)
  while companion/body/span agree — synchronize the name in TOML /
  generated headers via the usual census edits.
- H3: skip this address (fake fragment, overlay collision that is the
  real occupant, size/boundary disagreement, or no independent name).
- H4: the site is not evaluable this iteration (missing companion file,
  generated body, or TOML/section-4 row).

Discriminator: one static census, no game run.

```sh
# companion
grep -n 'spawnPlayerAtStCannonFire\|800D1248\|advancePlayerAtStLocomotion\|800D1578\|playerAtStInit\|800D1088' \
  ~/Documents/Tools/rogue_squadron64/symbol_files/mission_overlay.txt \
  ~/Documents/Tools/rogue_squadron64/symbol_files/menu_overlay.txt
# generated + TOML + overlay table
grep -n 'spawnPlayerAtStCannonFire\|func_800D1248\|0x800D1248\|advancePlayerAtStLocomotion\|func_800D1578\|0x800D1578' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl \
  syms/rogue_squadron.syms.toml
# body window in the owning funcs_*.c (expect funcs_37.c from s1696)
```

Expected splits:

- H1: all four sources already use `spawnPlayerAtStCannonFire` and size
  `0x330`; record confirmation; next candidate `func_800D1578` /
  `advancePlayerAtStLocomotion`.
- H2: rename a stale placeholder where the generated/TOML copy is stale
  (TOML is currently `func_800D1248` — likely this arm).
- H3: leave the current name and document why; pick the next contiguous
  mission function.
- H4: stop and write the missing artifact.

Do not expand into a second function in the same iteration.
