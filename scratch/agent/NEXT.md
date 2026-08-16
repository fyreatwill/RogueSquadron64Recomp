# NEXT work unit (s1704)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the exact generated-symbol census. Last-15 titles after s1703
include the s1698 retail-entry revisit, so the 15-title REVISIT gate
does not fire. Do not start another retail-entry or M4 experiment.

Candidate: `fake_func_800D2C98` at `0x800D2C98` (size `0x8`).
Companion names it `fake_func_800D2C98` (explicit leftover; the
following `func_800D2CA0` row was deleted as a duplicate of
`npcInitWithMotionParams`). Previous is `spawnScaledBootVec4Effect`
at `0x800D2C58`. Next companion / generated neighbor is
`npcInitWithMotionParams` at `0x800D2CA0` (TOML still `func_800D2CA0`).

Competing hypotheses and discriminator:

- H1: companion name, live generated body, exact
  `0x800D2C58`/`0x800D2CA0` boundaries, TOML size, and section-4 overlay
  span already agree — confirm and leave (or only correct a stale TOML
  placeholder).
- H2: the generated symbol is still `func_800D2C98` (or a wrong name)
  while companion/body/span agree — synchronize the name in TOML /
  generated headers via the usual census edits.
- H3: skip this address (not actually a leftover, overlay collision that
  is the real occupant, size/boundary disagreement, or no independent
  name).
- H4: the site is not evaluable this iteration (missing companion file,
  generated body, or TOML/section-4 row).

Discriminator: one static census, no game run.

```sh
# companion
grep -n 'fake_func_800D2C98\|800D2C98\|spawnScaledBootVec4Effect\|800D2C58\|npcInitWithMotionParams\|800D2CA0' \
  ~/Documents/Tools/rogue_squadron64/symbol_files/mission_overlay.txt \
  ~/Documents/Tools/rogue_squadron64/symbol_files/menu_overlay.txt
# generated + TOML + overlay table
grep -n 'fake_func_800D2C98\|func_800D2C98\|0x800D2C98\|spawnScaledBootVec4Effect\|func_800D2C58\|0x800D2C58\|npcInitWithMotionParams\|func_800D2CA0' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl \
  syms/rogue_squadron.syms.toml
# body window in the owning funcs_*.c (expect funcs_37.c from s1703)
```

Expected splits:

- H1: all four sources already use `fake_func_800D2C98` and size `0x8`;
  record confirmation; next candidate `npcInitWithMotionParams` at
  `0x800D2CA0`.
- H2: rename a stale placeholder where the generated/TOML copy is stale.
- H3: leave the current name and document why; pick the next contiguous
  mission function.
- H4: stop and write the missing artifact.

Do not expand into a second function in the same iteration.
