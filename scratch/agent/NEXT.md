# NEXT work unit (s1791)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the generated-symbol census at leftover `fake_func_800E71C8`
(`0x800E71C8`, size `0x8`). s1776 was the last mandatory REVISIT
(`selected H1 submitGfxFrame on the attract 1024`); last-15 titles
after s1790 include that revisit, so the all-sweep REVISIT gate
does not fire. Neighbor peek: companion, generated headers/body,
TOML, and section-4 already use the leftover name.

Competing hypotheses:

- H1: companion, generated body, TOML name/size, and overlay span already
  agree on leftover `fake_func_800E71C8` — confirm only.
- H2: generated code still carries placeholder `func_800E71C8` (or a
  stale alias) and needs a TOML + fixup rename, or TOML disagrees with
  generated/overlay.
- H3: overlay collision, a leftover splat disagreement, or size/boundary
  disagreement with the companion listing (expected size `0x8`:
  `0x800E71D0 - 0x800E71C8`, between `npcWaterCraftUpdate` and
  leftover `func_800E71D0`).
- H4: companion, generated body, TOML, or section-4 row is missing.

Exact commands (read-only census; no game run):

```
# companion
grep -n 'fake_func_800E71C8\|func_800E71C8\|800E71C8\|E71C8' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/*.txt
# generated
grep -n 'fake_func_800E71C8\|func_800E71C8\|0x800E71C8' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_39.c
# toml + overlay inl
grep -n '800E71C8\|fake_func_800E71C8\|func_800E71C8' \
  syms/rogue_squadron.syms.toml \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl
```

Expected splits:

- H1: all four sources already say `fake_func_800E71C8`,
  size `0x8`, previous `npcWaterCraftUpdate` / `0x800E614C`,
  next leftover `func_800E71D0` / `0x800E71D0`, no leftover
  `func_800E71C8` placeholder.
- H2: generated still `func_800E71C8`, or TOML disagrees with
  generated/overlay — rename in TOML and the fixup path.
- H3: menu/cinematic occupant, a leftover splat at this address, or
  size != `0x8`.
- H4: a required source is absent.

Do not reopen the attract-1024 six-entry, jump-table, or s1776
main-text 11-PC recipes. Next retail-entry revisit (when last-15 are
all sweep again) watches `submitGfxFrame` callers for the extra +105.
