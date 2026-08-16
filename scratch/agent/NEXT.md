# NEXT work unit (s1709)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the exact generated-symbol census. Last-15 titles after s1708
include the s1698 retail-entry revisit, so the 15-title REVISIT gate
does not fire. Do not start another retail-entry or M4 experiment.

Candidate: `npcShuttleHandleDestruction` at `0x800D33CC`
(size `0x4C8`). Companion names it
`npcShuttleHandleDestruction` ("Imperial Shuttle destruction.
Caller: npcShuttleUpdate"). Previous is
`npcTickEffectChannelWithSlotDispatch` at `0x800D3240`. Next companion
/ generated neighbor is `npcShuttleUpdate` at `0x800D3894`
(TOML already `npcShuttleUpdate`). Generated headers/overlays already
use the human name; TOML still has `func_800D33CC`.

Competing hypotheses and discriminator:

- H1: companion name, live generated body, exact
  `0x800D3240`/`0x800D3894` boundaries, TOML size, and section-4 overlay
  span already agree — confirm and leave (or only correct a stale TOML
  placeholder).
- H2: the generated symbol is still `func_800D33CC` (or a wrong name)
  while companion/body/span agree — synchronize the name in TOML /
  generated headers via the usual census edits.
- H3: skip this address (leftover/fake fragment, overlay collision that
  is the real occupant, size/boundary disagreement, or no independent
  name).
- H4: the site is not evaluable this iteration (missing companion file,
  generated body, or TOML/section-4 row).

Discriminator: one static census, no game run.

```sh
# companion
grep -n 'npcShuttleHandleDestruction\|800D33CC\|npcTickEffectChannelWithSlotDispatch\|800D3240\|npcShuttleUpdate\|800D3894' \
  ~/Documents/Tools/rogue_squadron64/symbol_files/mission_overlay.txt \
  ~/Documents/Tools/rogue_squadron64/symbol_files/menu_overlay.txt
# generated + TOML + overlay table
grep -n 'npcShuttleHandleDestruction\|func_800D33CC\|0x800D33CC\|npcTickEffectChannelWithSlotDispatch\|0x800D3240\|npcShuttleUpdate\|0x800D3894' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl \
  syms/rogue_squadron.syms.toml
# body window in the owning funcs_*.c (expect funcs_38.c from s1708)
```

Expected splits:

- H1: all four sources already use `npcShuttleHandleDestruction`
  and size `0x4C8`; record confirmation; next candidate
  `npcShuttleUpdate` at `0x800D3894` (already named — confirm or
  continue past it).
- H2: rename a stale placeholder where the generated/TOML copy is stale
  (TOML is currently `func_800D33CC`).
- H3: leave the current name and document why; pick the next contiguous
  mission function.
- H4: stop and write the missing artifact.

Do not expand into a second function in the same iteration.
