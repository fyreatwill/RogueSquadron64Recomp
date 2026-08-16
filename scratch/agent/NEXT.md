# NEXT work unit (s1683)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the exact generated-symbol census. Last-15 titles after s1682
include the s1682 retail-entry revisit, so the 15-title REVISIT gate
does not fire. Do not start another retail-entry or M4 experiment.

Candidate: `func_800CC9B8` / `tickAtAtAudioAndWeaponState` at
`0x800CC9B8` (size `0x164`). Companion next is
`processAtAtSubFeatureSlot` at `0x800CCB1C` (`0x800CC9B8 + 0x164`).
Previous mission function is `tickAtAtBodyTransform` at `0x800CC2AC`.

Competing hypotheses and discriminator:

- H1: companion name, live generated body, exact
  `0x800CC2AC`/`0x800CCB1C` boundaries, TOML size, and section-4 overlay
  span already agree — confirm and leave (or only correct a stale TOML
  placeholder).
- H2: the generated symbol is still `func_800CC9B8` (or a wrong name)
  while companion/body/span agree — synchronize the name in TOML /
  generated headers via the usual census edits.
- H3: skip this address (fake fragment, overlay collision that is the
  real occupant, size/boundary disagreement, or no independent name).
- H4: the site is not evaluable this iteration (missing companion file,
  generated body, or TOML/section-4 row).

Discriminator: one static census, no game run.

```sh
# companion
grep -n 'tickAtAtAudioAndWeaponState\|800CC9B8\|processAtAtSubFeatureSlot\|800CCB1C' \
  ~/Documents/Tools/rogue_squadron64/symbol_files/mission_overlay.txt \
  ~/Documents/Tools/rogue_squadron64/symbol_files/menu_overlay.txt
# generated + TOML + overlay table
grep -n 'tickAtAtAudioAndWeaponState\|func_800CC9B8\|0x800CC9B8' \
  RecompiledFuncs/funcs.h RecompiledFuncs/recomp_overlays.inl \
  rogue_squadron.toml 2>/dev/null
# body window in the owning funcs_*.c (expect funcs_37.c from s1681)
```

Expected splits:

- H1: all four sources already use `tickAtAtAudioAndWeaponState` and
  size `0x164`; record confirmation; next candidate
  `processAtAtSubFeatureSlot`.
- H2: rename the stale `func_800CC9B8` placeholder to
  `tickAtAtAudioAndWeaponState` where the generated/TOML copy is stale.
- H3: leave `func_*` and document why; pick the next address.
- H4: stop and write the missing artifact.

Do not expand into a second function in the same iteration.
