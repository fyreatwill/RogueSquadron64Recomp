# NEXT work unit (s1691)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the exact generated-symbol census. Last-15 titles after s1690
include the s1682 retail-entry revisit, so the 15-title REVISIT gate
does not fire. Do not start another retail-entry or M4 experiment.

Candidate: `func_800CF09C` / `tickAtStCannonFireEffect` at
`0x800CF09C` (size `0x170`). Companion and generated headers already
use `tickAtStCannonFireEffect`; the project TOML still carries the
placeholder `func_800CF09C`. Previous is `advanceAtStEffectPhaseSound`
at `0x800CEF20`. Next companion neighbor is `updateAtStBodyKinematics`
at `0x800CF20C`.

Competing hypotheses and discriminator:

- H1: companion name, live generated body, exact
  `0x800CEF20`/`0x800CF20C` boundaries, TOML size, and section-4 overlay
  span already agree — confirm and leave (or only correct a stale TOML
  placeholder).
- H2: the generated symbol is still `func_800CF09C` (or a wrong name)
  while companion/body/span agree — synchronize the name in TOML /
  generated headers via the usual census edits.
- H3: skip this address (fake fragment, overlay collision that is the
  real occupant, size/boundary disagreement, or no independent name).
- H4: the site is not evaluable this iteration (missing companion file,
  generated body, or TOML/section-4 row).

Discriminator: one static census, no game run.

```sh
# companion
grep -n 'tickAtStCannonFireEffect\|800CF09C\|updateAtStBodyKinematics\|800CF20C' \
  ~/Documents/Tools/rogue_squadron64/symbol_files/mission_overlay.txt \
  ~/Documents/Tools/rogue_squadron64/symbol_files/menu_overlay.txt
# generated + TOML + overlay table
grep -n 'tickAtStCannonFireEffect\|func_800CF09C\|0x800CF09C\|updateAtStBodyKinematics\|func_800CF20C\|0x800CF20C' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl \
  syms/rogue_squadron.syms.toml
# body window in the owning funcs_*.c (expect funcs_37.c from s1690)
```

Expected splits:

- H1: all four sources already use `tickAtStCannonFireEffect` and
  size `0x170`; record confirmation; next candidate
  `func_800CF20C` / `updateAtStBodyKinematics`.
- H2: rename a stale placeholder where the generated/TOML copy is stale.
- H3: leave the current name and document why; pick the next contiguous
  mission function.
- H4: stop and write the missing artifact.

Do not expand into a second function in the same iteration.
