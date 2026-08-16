# NEXT work unit (s1687)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the exact generated-symbol census. Last-15 titles after s1686
include the s1682 retail-entry revisit, so the 15-title REVISIT gate
does not fire. Do not start another retail-entry or M4 experiment.

Candidate: `func_800CD558` / `updateAtAtLegArticulation` at
`0x800CD558` (size `0x1C4`). Companion next is
`npcAtAtUpdate` at `0x800CD71C` (`0x800CD558 + 0x1C4`).
Previous mission function is `spawnAtAtFootstepDustBurst` at
`0x800CD38C`.

Competing hypotheses and discriminator:

- H1: companion name, live generated body, exact
  `0x800CD38C`/`0x800CD71C` boundaries, TOML size, and section-4 overlay
  span already agree — confirm and leave (or only correct a stale TOML
  placeholder).
- H2: the generated symbol is still `func_800CD558` (or a wrong name)
  while companion/body/span agree — synchronize the name in TOML /
  generated headers via the usual census edits.
- H3: skip this address (fake fragment, overlay collision that is the
  real occupant, size/boundary disagreement, or no independent name).
- H4: the site is not evaluable this iteration (missing companion file,
  generated body, or TOML/section-4 row).

Discriminator: one static census, no game run.

```sh
# companion
grep -n 'updateAtAtLegArticulation\|800CD558\|npcAtAtUpdate\|800CD71C' \
  ~/Documents/Tools/rogue_squadron64/symbol_files/mission_overlay.txt \
  ~/Documents/Tools/rogue_squadron64/symbol_files/menu_overlay.txt
# generated + TOML + overlay table
grep -n 'updateAtAtLegArticulation\|func_800CD558\|0x800CD558' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl \
  syms/rogue_squadron.syms.toml
# body window in the owning funcs_*.c (expect funcs_37.c from s1686)
```

Expected splits:

- H1: all four sources already use `updateAtAtLegArticulation` and
  size `0x1C4`; record confirmation; next candidate
  `npcAtAtUpdate`.
- H2: rename the stale `func_800CD558` placeholder to
  `updateAtAtLegArticulation` where the generated/TOML copy is stale.
- H3: leave `func_*` and document why; pick the next address.
- H4: stop and write the missing artifact.

Do not expand into a second function in the same iteration.
