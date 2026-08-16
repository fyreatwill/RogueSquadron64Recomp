# NEXT work unit (s1689)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the exact generated-symbol census. Last-15 titles after s1688
include the s1682 retail-entry revisit, so the 15-title REVISIT gate
does not fire. Do not start another retail-entry or M4 experiment.

Candidate: `fake_func_800CEF1C` at `0x800CEF1C` (size `0x4`).
Generated body is a single `sw $s1, 0x44($sp)` fragment.
Companion/TOML next neighbor is `func_800CEF20` /
`advanceAtStEffectPhaseSound` at `0x800CEF20` (size `0x17C`).
Previous mission function is `npcAtAtUpdate` at `0x800CD71C`.

Competing hypotheses and discriminator:

- H1: companion name, live generated body, exact
  `0x800CD71C`/`0x800CEF20` boundaries, TOML size, and section-4 overlay
  span already agree — confirm and leave (or only correct a stale TOML
  placeholder).
- H2: the generated symbol is still `func_800CEF1C` (or a wrong name)
  while companion/body/span agree — synchronize the name in TOML /
  generated headers via the usual census edits.
- H3: skip this address (fake fragment, overlay collision that is the
  real occupant, size/boundary disagreement, or no independent name).
- H4: the site is not evaluable this iteration (missing companion file,
  generated body, or TOML/section-4 row).

Discriminator: one static census, no game run.

```sh
# companion
grep -n 'fake_func_800CEF1C\|800CEF1C\|advanceAtStEffectPhaseSound\|800CEF20' \
  ~/Documents/Tools/rogue_squadron64/symbol_files/mission_overlay.txt \
  ~/Documents/Tools/rogue_squadron64/symbol_files/menu_overlay.txt
# generated + TOML + overlay table
grep -n 'fake_func_800CEF1C\|func_800CEF1C\|0x800CEF1C\|advanceAtStEffectPhaseSound\|func_800CEF20\|0x800CEF20' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl \
  syms/rogue_squadron.syms.toml
# body window in the owning funcs_*.c (expect funcs_37.c from s1688)
```

Expected splits:

- H1: all four sources already use `fake_func_800CEF1C` and size `0x4`;
  record confirmation; next candidate `func_800CEF20` /
  `advanceAtStEffectPhaseSound`.
- H2: rename a stale placeholder where the generated/TOML copy is stale.
- H3: leave `fake_func_*` and document why (4-byte leftover store
  between `npcAtAtUpdate` and `advanceAtStEffectPhaseSound`); pick
  `func_800CEF20` / `advanceAtStEffectPhaseSound` next.
- H4: stop and write the missing artifact.

Do not expand into a second function in the same iteration.
