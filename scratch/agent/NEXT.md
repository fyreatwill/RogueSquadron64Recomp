# NEXT work unit (s1706)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the exact generated-symbol census. Last-15 titles after s1705
include the s1698 retail-entry revisit, so the 15-title REVISIT gate
does not fire. Do not start another retail-entry or M4 experiment.

Candidate: `npcTickEffectChannelA` at `0x800D2EE0` (size `0x19C`).
Companion names it `npcTickEffectChannelA` ("per-frame visual/SFX
channel: HMT tex + attach-pos + progress-channel + cue + 3D sound").
Previous is `npcInitWithMotionParams` at `0x800D2CA0`. Next companion
/ generated neighbor is `npcTickEffectChannelB` at `0x800D307C`
(TOML still `func_800D307C`). Generated headers/overlays already use
the human name; TOML still has `func_800D2EE0`.

Competing hypotheses and discriminator:

- H1: companion name, live generated body, exact
  `0x800D2CA0`/`0x800D307C` boundaries, TOML size, and section-4 overlay
  span already agree — confirm and leave (or only correct a stale TOML
  placeholder).
- H2: the generated symbol is still `func_800D2EE0` (or a wrong name)
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
grep -n 'npcTickEffectChannelA\|800D2EE0\|npcInitWithMotionParams\|800D2CA0\|npcTickEffectChannelB\|800D307C' \
  ~/Documents/Tools/rogue_squadron64/symbol_files/mission_overlay.txt \
  ~/Documents/Tools/rogue_squadron64/symbol_files/menu_overlay.txt
# generated + TOML + overlay table
grep -n 'npcTickEffectChannelA\|func_800D2EE0\|0x800D2EE0\|npcInitWithMotionParams\|0x800D2CA0\|npcTickEffectChannelB\|func_800D307C' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl \
  syms/rogue_squadron.syms.toml
# body window in the owning funcs_*.c (expect funcs_37.c from s1705)
```

Expected splits:

- H1: all four sources already use `npcTickEffectChannelA` and size
  `0x19C`; record confirmation; next candidate `npcTickEffectChannelB`
  at `0x800D307C`.
- H2: rename a stale placeholder where the generated/TOML copy is stale
  (TOML is currently `func_800D2EE0`).
- H3: leave the current name and document why; pick the next contiguous
  mission function.
- H4: stop and write the missing artifact.

Do not expand into a second function in the same iteration.
