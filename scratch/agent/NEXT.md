# NEXT work unit (s1708)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the exact generated-symbol census. Last-15 titles after s1707
include the s1698 retail-entry revisit, so the 15-title REVISIT gate
does not fire. Do not start another retail-entry or M4 experiment.

Candidate: `npcTickEffectChannelWithSlotDispatch` at `0x800D3240`
(size `0x18C`). Companion names it
`npcTickEffectChannelWithSlotDispatch` ("effect-channel tick that
also fans out via slotDispatcherIter"). Previous is
`npcTickEffectChannelB` at `0x800D307C`. Next companion / generated
neighbor is `npcShuttleHandleDestruction` at `0x800D33CC`
(TOML still `func_800D33CC`). Generated headers/overlays already use
the human name; TOML still has `func_800D3240`.

Competing hypotheses and discriminator:

- H1: companion name, live generated body, exact
  `0x800D307C`/`0x800D33CC` boundaries, TOML size, and section-4 overlay
  span already agree — confirm and leave (or only correct a stale TOML
  placeholder).
- H2: the generated symbol is still `func_800D3240` (or a wrong name)
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
grep -n 'npcTickEffectChannelWithSlotDispatch\|800D3240\|npcTickEffectChannelB\|800D307C\|npcShuttleHandleDestruction\|800D33CC' \
  ~/Documents/Tools/rogue_squadron64/symbol_files/mission_overlay.txt \
  ~/Documents/Tools/rogue_squadron64/symbol_files/menu_overlay.txt
# generated + TOML + overlay table
grep -n 'npcTickEffectChannelWithSlotDispatch\|func_800D3240\|0x800D3240\|npcTickEffectChannelB\|0x800D307C\|npcShuttleHandleDestruction\|func_800D33CC' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl \
  syms/rogue_squadron.syms.toml
# body window in the owning funcs_*.c (expect funcs_37.c from s1707)
```

Expected splits:

- H1: all four sources already use `npcTickEffectChannelWithSlotDispatch`
  and size `0x18C`; record confirmation; next candidate
  `npcShuttleHandleDestruction` at `0x800D33CC`.
- H2: rename a stale placeholder where the generated/TOML copy is stale
  (TOML is currently `func_800D3240`).
- H3: leave the current name and document why; pick the next contiguous
  mission function.
- H4: stop and write the missing artifact.

Do not expand into a second function in the same iteration.
