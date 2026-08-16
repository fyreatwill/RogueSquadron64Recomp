# NEXT work unit (s1711)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the exact generated-symbol census. Last-15 titles after s1710
still include the s1698 retail-entry revisit, so the 15-title REVISIT
gate does not fire. Do not start another retail-entry or M4 experiment.

Candidate: `fake_func_800D4EC4` at `0x800D4EC4` (size `0xC`).
Companion names it `fake_func_800D4EC4` (segment:mission_overlay);
the comment records `func_800D4ED0` deleted s432 as a duplicate of
`npcInitChildLinkedToParent`. Previous is `npcShuttleUpdate` at
`0x800D3894`. Next generated neighbor is `npcInitChildLinkedToParent`
at `0x800D4ED0` (TOML still `func_800D4ED0`). Generated headers/overlays
already use the fake name.

Competing hypotheses and discriminator:

- H1: companion name, live generated fragment, exact
  `0x800D3894`/`0x800D4ED0` boundaries, TOML size, and section-4 overlay
  span already agree — confirm and leave.
- H2: the generated symbol is still `func_800D4EC4` (or a wrong name)
  while companion/body/span agree — synchronize the name in TOML /
  generated headers via the usual census edits.
- H3: skip this address (leftover/fake fragment already classified, overlay
  collision that is the real occupant, size/boundary disagreement, or no
  independent name). The companion already labels it `fake_func_*`; H3
  here means the fragment is not the classified leftover or the span is
  wrong.
- H4: the site is not evaluable this iteration (missing companion file,
  generated body, or TOML/section-4 row).

Discriminator: one static census, no game run.

```sh
# companion
grep -n 'fake_func_800D4EC4\|800D4EC4\|npcInitChildLinkedToParent\|800D4ED0\|npcShuttleUpdate\|800D3894' \
  ~/Documents/Tools/rogue_squadron64/symbol_files/mission_overlay.txt \
  ~/Documents/Tools/rogue_squadron64/symbol_files/menu_overlay.txt
# generated + TOML + overlay table
grep -n 'fake_func_800D4EC4\|func_800D4EC4\|0x800D4EC4\|npcInitChildLinkedToParent\|func_800D4ED0\|0x800D4ED0\|npcShuttleUpdate\|0x800D3894' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl \
  syms/rogue_squadron.syms.toml
# body window in the owning funcs_*.c (expect funcs_38.c)
```

Expected splits:

- H1: all four sources already use `fake_func_800D4EC4` and size
  `0xC`; record confirmation; next candidate
  `npcInitChildLinkedToParent` / `func_800D4ED0` at `0x800D4ED0`.
- H2: rename a stale placeholder where the generated/TOML copy is stale.
- H3: leave the current name and document why; pick the next contiguous
  mission function.
- H4: stop and write the missing artifact.

Do not expand into a second function in the same iteration.
