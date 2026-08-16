# NEXT work unit (s1713)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the exact generated-symbol census. Last-15 titles after s1712
still include the s1698 retail-entry revisit, so the 15-title REVISIT
gate does not fire. Do not start another retail-entry or M4 experiment.

Candidate: `advanceNpcSpinOrientation` at `0x800D5078` (size `0x190`).
Companion names it `advanceNpcSpinOrientation` (segment:mission_overlay);
generated headers/overlays already use that name. TOML still carries
`func_800D5078`. Previous is `npcInitChildLinkedToParent` at `0x800D4ED0`.
Next generated neighbor is `npcDebrisFieldUpdate` at `0x800D5208`
(TOML still `func_800D5208`).

Competing hypotheses and discriminator:

- H1: companion name, live generated body, exact
  `0x800D4ED0`/`0x800D5208` boundaries, TOML size, and section-4 overlay
  span already agree — confirm and leave.
- H2: the generated symbol is still `func_800D5078` (or a wrong name)
  while companion/body/span agree — synchronize the name in TOML /
  generated headers via the usual census edits. The likely arm: TOML
  is the only stale copy.
- H3: skip this address (leftover/fake fragment already classified, overlay
  collision that is the real occupant, size/boundary disagreement, or no
  independent name).
- H4: the site is not evaluable this iteration (missing companion file,
  generated body, or TOML/section-4 row).

Discriminator: one static census, no game run.

```sh
# companion
grep -n 'advanceNpcSpinOrientation\|800D5078\|npcDebrisFieldUpdate\|800D5208\|npcInitChildLinkedToParent\|800D4ED0' \
  ~/Documents/Tools/rogue_squadron64/symbol_files/mission_overlay.txt \
  ~/Documents/Tools/rogue_squadron64/symbol_files/menu_overlay.txt
# generated + TOML + overlay table
grep -n 'advanceNpcSpinOrientation\|func_800D5078\|0x800D5078\|npcDebrisFieldUpdate\|func_800D5208\|0x800D5208\|npcInitChildLinkedToParent\|0x800D4ED0' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl \
  syms/rogue_squadron.syms.toml
# body window in the owning funcs_*.c (expect funcs_38.c)
```

Expected splits:

- H1: all four sources already use `advanceNpcSpinOrientation` and size
  `0x190`; record confirmation; next candidate
  `npcDebrisFieldUpdate` / `func_800D5208` at `0x800D5208`.
- H2: rename a stale placeholder where the generated/TOML copy is stale
  (likely TOML `func_800D5078` only).
- H3: leave the current name and document why; pick the next contiguous
  mission function.
- H4: stop and write the missing artifact.

Do not expand into a second function in the same iteration.
