# NEXT work unit (s1701)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the exact generated-symbol census. Last-15 titles after s1700
include the s1698 retail-entry revisit, so the 15-title REVISIT gate
does not fire. Do not start another retail-entry or M4 experiment.

Candidate: `playerAtStUpdate` at `0x800D2208` (size `0x954`).
Companion names it `playerAtStUpdate`. TOML already has
`playerAtStUpdate`. Previous is `updatePlayerAtStBehavior` at
`0x800D1730`. Next companion / generated neighbor is
`npcInitFromTemplate` at `0x800D2B5C` (TOML still `func_800D2B5C`).

Competing hypotheses and discriminator:

- H1: companion name, live generated body, exact
  `0x800D1730`/`0x800D2B5C` boundaries, TOML size, and section-4 overlay
  span already agree — confirm and leave (or only correct a stale TOML
  placeholder).
- H2: the generated symbol is still `func_800D2208` (or a wrong name)
  while companion/body/span agree — synchronize the name in TOML /
  generated headers via the usual census edits.
- H3: skip this address (fake fragment, overlay collision that is the
  real occupant, size/boundary disagreement, or no independent name).
- H4: the site is not evaluable this iteration (missing companion file,
  generated body, or TOML/section-4 row).

Discriminator: one static census, no game run.

```sh
# companion
grep -n 'playerAtStUpdate\|800D2208\|npcInitFromTemplate\|800D2B5C\|updatePlayerAtStBehavior\|800D1730' \
  ~/Documents/Tools/rogue_squadron64/symbol_files/mission_overlay.txt \
  ~/Documents/Tools/rogue_squadron64/symbol_files/menu_overlay.txt
# generated + TOML + overlay table
grep -n 'playerAtStUpdate\|func_800D2208\|0x800D2208\|npcInitFromTemplate\|func_800D2B5C\|0x800D2B5C' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl \
  syms/rogue_squadron.syms.toml
# body window in the owning funcs_*.c (expect funcs_37.c from s1700)
```

Expected splits:

- H1: all four sources already use `playerAtStUpdate` and
  size `0x954`; record confirmation; next candidate
  `npcInitFromTemplate` at `0x800D2B5C`.
- H2: rename a stale placeholder where the generated/TOML copy is stale.
- H3: leave the current name and document why; pick the next contiguous
  mission function.
- H4: stop and write the missing artifact.

Do not expand into a second function in the same iteration.
