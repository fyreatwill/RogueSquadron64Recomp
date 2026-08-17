# NEXT work unit (s1790)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the generated-symbol census at `npcWaterCraftUpdate`
(`0x800E614C`, size `0x107C`). s1776 was the last mandatory REVISIT
(`selected H1 submitGfxFrame on the attract 1024`); last-15 titles
after s1789 include that revisit, so the all-sweep REVISIT gate
does not fire. Neighbor peek: companion, generated headers/body,
TOML, and section-4 already use the human name.

Competing hypotheses:

- H1: companion, generated body, TOML name/size, and overlay span already
  agree on `npcWaterCraftUpdate` — confirm only.
- H2: generated code still carries placeholder `func_800E614C` (or a
  stale alias) and needs a TOML + fixup rename, or TOML disagrees with
  generated/overlay.
- H3: overlay collision, a leftover splat disagreement, or size/boundary
  disagreement with the companion listing (expected size `0x107C`:
  `0x800E71C8 - 0x800E614C`, between `npcWaterCraftHandleDestruction`
  and leftover `fake_func_800E71C8`).
- H4: companion, generated body, TOML, or section-4 row is missing.

Exact commands (read-only census; no game run):

```
# companion
grep -n 'npcWaterCraftUpdate\|func_800E614C\|800E614C\|E614C' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/*.txt
# generated
grep -n 'npcWaterCraftUpdate\|func_800E614C\|0x800E614C' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_39.c
# toml + overlay inl
grep -n '800E614C\|npcWaterCraftUpdate\|func_800E614C' \
  syms/rogue_squadron.syms.toml \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl
```

Expected splits:

- H1: all four sources already say `npcWaterCraftUpdate`,
  size `0x107C`, previous `npcWaterCraftHandleDestruction` /
  `0x800E5B38`, next leftover `fake_func_800E71C8` / `0x800E71C8`,
  no leftover `func_800E614C` placeholder.
- H2: generated still `func_800E614C`, or TOML disagrees with
  generated/overlay — rename in TOML and the fixup path.
- H3: menu/cinematic occupant, a leftover splat at this address, or
  size != `0x107C`.
- H4: a required source is absent.

Do not reopen the attract-1024 six-entry, jump-table, or s1776
main-text 11-PC recipes. Next retail-entry revisit (when last-15 are
all sweep again) watches `submitGfxFrame` callers for the extra +105.
