# NEXT work unit (s1710)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the exact generated-symbol census. Last-15 titles after s1709
still include the s1698 retail-entry revisit, so the 15-title REVISIT
gate does not fire. Do not start another retail-entry or M4 experiment.

Candidate: `npcShuttleUpdate` at `0x800D3894` (size `0x1630`).
Companion names it `npcShuttleUpdate` (segment:mission_overlay).
Previous is `npcShuttleHandleDestruction` at `0x800D33CC`. Next
generated neighbor is `fake_func_800D4EC4` at `0x800D4EC4` (TOML
already `fake_func_800D4EC4`). Generated headers/overlays and TOML
already use the human name.

Competing hypotheses and discriminator:

- H1: companion name, live generated body, exact
  `0x800D33CC`/`0x800D4EC4` boundaries, TOML size, and section-4 overlay
  span already agree — confirm and leave.
- H2: the generated symbol is still `func_800D3894` (or a wrong name)
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
grep -n 'npcShuttleUpdate\|800D3894\|npcShuttleHandleDestruction\|800D33CC\|fake_func_800D4EC4\|800D4EC4' \
  ~/Documents/Tools/rogue_squadron64/symbol_files/mission_overlay.txt \
  ~/Documents/Tools/rogue_squadron64/symbol_files/menu_overlay.txt
# generated + TOML + overlay table
grep -n 'npcShuttleUpdate\|func_800D3894\|0x800D3894\|npcShuttleHandleDestruction\|0x800D33CC\|fake_func_800D4EC4\|0x800D4EC4' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl \
  syms/rogue_squadron.syms.toml
# body window in the owning funcs_*.c (expect funcs_38.c)
```

Expected splits:

- H1: all four sources already use `npcShuttleUpdate` and size
  `0x1630`; record confirmation; next candidate
  `fake_func_800D4EC4` at `0x800D4EC4`.
- H2: rename a stale placeholder where the generated/TOML copy is stale.
- H3: leave the current name and document why; pick the next contiguous
  mission function.
- H4: stop and write the missing artifact.

Do not expand into a second function in the same iteration.
