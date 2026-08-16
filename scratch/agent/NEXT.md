# NEXT work unit (s1688)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the exact generated-symbol census. Last-15 titles after s1687
include the s1682 retail-entry revisit, so the 15-title REVISIT gate
does not fire. Do not start another retail-entry or M4 experiment.

Candidate: `npcAtAtUpdate` at `0x800CD71C` (size `0x1800`).
Companion next/TOML neighbor is `fake_func_800CEF1C` at
`0x800CEF1C` (`0x800CD71C + 0x1800`), then
`func_800CEF20` / `advanceAtStEffectPhaseSound`.
Previous mission function is `updateAtAtLegArticulation` at
`0x800CD558`.

Competing hypotheses and discriminator:

- H1: companion name, live generated body, exact
  `0x800CD558`/`0x800CEF1C` boundaries, TOML size, and section-4 overlay
  span already agree — confirm and leave (or only correct a stale TOML
  placeholder).
- H2: the generated symbol is still `func_800CD71C` (or a wrong name)
  while companion/body/span agree — synchronize the name in TOML /
  generated headers via the usual census edits.
- H3: skip this address (fake fragment, overlay collision that is the
  real occupant, size/boundary disagreement, or no independent name).
- H4: the site is not evaluable this iteration (missing companion file,
  generated body, or TOML/section-4 row).

Discriminator: one static census, no game run.

```sh
# companion
grep -n 'npcAtAtUpdate\|800CD71C\|fake_func_800CEF1C\|800CEF1C\|advanceAtStEffectPhaseSound\|800CEF20' \
  ~/Documents/Tools/rogue_squadron64/symbol_files/mission_overlay.txt \
  ~/Documents/Tools/rogue_squadron64/symbol_files/menu_overlay.txt
# generated + TOML + overlay table
grep -n 'npcAtAtUpdate\|func_800CD71C\|0x800CD71C' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl \
  syms/rogue_squadron.syms.toml
# body window in the owning funcs_*.c (expect funcs_37.c from s1687)
```

Expected splits:

- H1: all four sources already use `npcAtAtUpdate` and size `0x1800`;
  record confirmation; next candidate `fake_func_800CEF1C` /
  `func_800CEF20` / `advanceAtStEffectPhaseSound`.
- H2: rename the stale `func_800CD71C` placeholder to
  `npcAtAtUpdate` where the generated/TOML copy is stale.
- H3: leave `func_*` and document why; pick the next address.
- H4: stop and write the missing artifact.

Do not expand into a second function in the same iteration.
