# NEXT work unit (s1685)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the exact generated-symbol census. Last-15 titles after s1684
include the s1682 retail-entry revisit, so the 15-title REVISIT gate
does not fire. Do not start another retail-entry or M4 experiment.

Candidate: `func_800CCC98` / `npcAtAtHandleDestruction` at
`0x800CCC98` (size `0x6F4`). Companion next is
`spawnAtAtFootstepDustBurst` at `0x800CD38C` (`0x800CCC98 + 0x6F4`).
Previous mission function is `processAtAtSubFeatureSlot` at
`0x800CCB1C`.

Competing hypotheses and discriminator:

- H1: companion name, live generated body, exact
  `0x800CCB1C`/`0x800CD38C` boundaries, TOML size, and section-4 overlay
  span already agree — confirm and leave (or only correct a stale TOML
  placeholder).
- H2: the generated symbol is still `func_800CCC98` (or a wrong name)
  while companion/body/span agree — synchronize the name in TOML /
  generated headers via the usual census edits.
- H3: skip this address (fake fragment, overlay collision that is the
  real occupant, size/boundary disagreement, or no independent name).
- H4: the site is not evaluable this iteration (missing companion file,
  generated body, or TOML/section-4 row).

Discriminator: one static census, no game run.

```sh
# companion
grep -n 'npcAtAtHandleDestruction\|800CCC98\|spawnAtAtFootstepDustBurst\|800CD38C' \
  ~/Documents/Tools/rogue_squadron64/symbol_files/mission_overlay.txt \
  ~/Documents/Tools/rogue_squadron64/symbol_files/menu_overlay.txt
# generated + TOML + overlay table
grep -n 'npcAtAtHandleDestruction\|func_800CCC98\|0x800CCC98' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl \
  syms/rogue_squadron.syms.toml
# body window in the owning funcs_*.c (expect funcs_37.c from s1684)
```

Expected splits:

- H1: all four sources already use `npcAtAtHandleDestruction` and
  size `0x6F4`; record confirmation; next candidate
  `spawnAtAtFootstepDustBurst`.
- H2: rename the stale `func_800CCC98` placeholder to
  `npcAtAtHandleDestruction` where the generated/TOML copy is stale.
- H3: leave `func_*` and document why; pick the next address.
- H4: stop and write the missing artifact.

Do not expand into a second function in the same iteration.
