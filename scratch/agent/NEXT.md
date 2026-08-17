# NEXT work unit (s1788)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the generated-symbol census at `tickStructureWithDestructionAndChildren`
(`0x800E56AC`, size `0x48C`). s1776 was the last mandatory REVISIT
(`selected H1 submitGfxFrame on the attract 1024`); last-15 titles
after s1787 include that revisit, so the all-sweep REVISIT gate
does not fire. Neighbor peek: companion, generated headers/body, and
section-4 already use the human name; TOML is still `func_800E56AC`.

Competing hypotheses:

- H1: companion, generated body, TOML name/size, and overlay span already
  agree on `tickStructureWithDestructionAndChildren` — confirm only.
- H2: generated code still carries placeholder `func_800E56AC` (or a
  stale alias) and needs a TOML + fixup rename, or TOML disagrees with
  generated/overlay (expected: TOML still `func_800E56AC`).
- H3: overlay collision, a leftover splat disagreement, or size/boundary
  disagreement with the companion listing (expected size `0x48C`:
  `0x800E5B38 - 0x800E56AC`, between `tickCraftSplineOrientationVariant`
  and `npcWaterCraftHandleDestruction` / leftover `func_800E5B38`).
- H4: companion, generated body, TOML, or section-4 row is missing.

Exact commands (read-only census; no game run):

```
# companion
grep -n 'tickStructureWithDestructionAndChildren\|func_800E56AC\|800E56AC\|E56AC' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/*.txt
# generated
grep -n 'tickStructureWithDestructionAndChildren\|func_800E56AC\|0x800E56AC' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_39.c
# toml + overlay inl
grep -n '800E56AC\|tickStructureWithDestructionAndChildren\|func_800E56AC' \
  syms/rogue_squadron.syms.toml \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl
```

Expected splits:

- H1: all four sources already say `tickStructureWithDestructionAndChildren`,
  size `0x48C`, previous `tickCraftSplineOrientationVariant` / `0x800E4DC0`,
  next `npcWaterCraftHandleDestruction` / leftover `func_800E5B38` /
  `0x800E5B38`, no leftover `func_800E56AC` placeholder.
- H2: generated still `func_800E56AC`, or TOML disagrees with
  generated/overlay — rename in TOML and the fixup path.
- H3: menu/cinematic occupant, a leftover splat at this address, or
  size != `0x48C`.
- H4: a required source is absent.

Do not reopen the attract-1024 six-entry, jump-table, or s1776
main-text 11-PC recipes. Next retail-entry revisit (when last-15 are
all sweep again) watches `submitGfxFrame` callers for the extra +105.
