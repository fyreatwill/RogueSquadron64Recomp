# NEXT work unit (s1699)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the exact generated-symbol census. Last-15 titles after s1698
include the s1698 retail-entry revisit, so the 15-title REVISIT gate
does not fire. Do not start another retail-entry or M4 experiment.

Candidate: `advancePlayerAtStLocomotion` at `0x800D1578` (size `0x1B8`).
Companion names it `advancePlayerAtStLocomotion`. TOML still has
placeholder `func_800D1578`. Previous is `spawnPlayerAtStCannonFire`
at `0x800D1248`. Next companion / generated neighbor is
`updatePlayerAtStBehavior` at `0x800D1730` (TOML still `func_800D1730`;
`playerAtStUpdate` is later at `0x800D2208`).

Competing hypotheses and discriminator:

- H1: companion name, live generated body, exact
  `0x800D1248`/`0x800D1730` boundaries, TOML size, and section-4 overlay
  span already agree — confirm and leave (or only correct a stale TOML
  placeholder).
- H2: the generated symbol is still `func_800D1578` (or a wrong name)
  while companion/body/span agree — synchronize the name in TOML /
  generated headers via the usual census edits.
- H3: skip this address (fake fragment, overlay collision that is the
  real occupant, size/boundary disagreement, or no independent name).
- H4: the site is not evaluable this iteration (missing companion file,
  generated body, or TOML/section-4 row).

Discriminator: one static census, no game run.

```sh
# companion
grep -n 'advancePlayerAtStLocomotion\|800D1578\|updatePlayerAtStBehavior\|800D1730\|spawnPlayerAtStCannonFire\|800D1248\|playerAtStUpdate\|800D2208' \
  ~/Documents/Tools/rogue_squadron64/symbol_files/mission_overlay.txt \
  ~/Documents/Tools/rogue_squadron64/symbol_files/menu_overlay.txt
# generated + TOML + overlay table
grep -n 'advancePlayerAtStLocomotion\|func_800D1578\|0x800D1578\|updatePlayerAtStBehavior\|func_800D1730\|0x800D1730' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl \
  syms/rogue_squadron.syms.toml
# body window in the owning funcs_*.c (expect funcs_37.c from s1697)
```

Expected splits:

- H1: all four sources already use `advancePlayerAtStLocomotion` and
  size `0x1B8`; record confirmation; next candidate `func_800D1730` /
  `updatePlayerAtStBehavior`.
- H2: rename a stale placeholder where the generated/TOML copy is stale
  (TOML is currently `func_800D1578` — likely this arm).
- H3: leave the current name and document why; pick the next contiguous
  mission function.
- H4: stop and write the missing artifact.

Do not expand into a second function in the same iteration.
