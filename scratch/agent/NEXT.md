# NEXT work unit (s1707)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the exact generated-symbol census. Last-15 titles after s1706
include the s1698 retail-entry revisit, so the 15-title REVISIT gate
does not fire. Do not start another retail-entry or M4 experiment.

Candidate: `npcTickEffectChannelB` at `0x800D307C` (size `0x1C4`).
Companion names it `npcTickEffectChannelB` ("effect-channel tick
variant (HMT tex + cue + 3D sound)"). Previous is
`npcTickEffectChannelA` at `0x800D2EE0`. Next companion / generated
neighbor is `npcTickEffectChannelWithSlotDispatch` at `0x800D3240`
(TOML still `func_800D3240`). Generated headers/overlays already use
the human name; TOML still has `func_800D307C`.

Competing hypotheses and discriminator:

- H1: companion name, live generated body, exact
  `0x800D2EE0`/`0x800D3240` boundaries, TOML size, and section-4 overlay
  span already agree — confirm and leave (or only correct a stale TOML
  placeholder).
- H2: the generated symbol is still `func_800D307C` (or a wrong name)
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
grep -n 'npcTickEffectChannelB\|800D307C\|npcTickEffectChannelA\|800D2EE0\|npcTickEffectChannelWithSlotDispatch\|800D3240' \
  ~/Documents/Tools/rogue_squadron64/symbol_files/mission_overlay.txt \
  ~/Documents/Tools/rogue_squadron64/symbol_files/menu_overlay.txt
# generated + TOML + overlay table
grep -n 'npcTickEffectChannelB\|func_800D307C\|0x800D307C\|npcTickEffectChannelA\|0x800D2EE0\|npcTickEffectChannelWithSlotDispatch\|func_800D3240' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl \
  syms/rogue_squadron.syms.toml
# body window in the owning funcs_*.c (expect funcs_37.c from s1706)
```

Expected splits:

- H1: all four sources already use `npcTickEffectChannelB` and size
  `0x1C4`; record confirmation; next candidate
  `npcTickEffectChannelWithSlotDispatch` at `0x800D3240`.
- H2: rename a stale placeholder where the generated/TOML copy is stale
  (TOML is currently `func_800D307C`).
- H3: leave the current name and document why; pick the next contiguous
  mission function.
- H4: stop and write the missing artifact.

Do not expand into a second function in the same iteration.
