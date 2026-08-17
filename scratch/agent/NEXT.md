# NEXT work unit (s1780)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the generated-symbol census at `handleRayShieldedNpcDestroy`
(`0x800E4070`, size `0x40C`). s1776 was the last mandatory REVISIT
(`selected H1 submitGfxFrame on the attract 1024`); last-15 titles
after s1779 include that revisit, so the all-sweep REVISIT gate does
not fire. Neighbor peek: TOML is still `func_800E4070` while generated
headers/body and section-4 already use the human name.

Competing hypotheses:

- H1: companion, generated body, TOML name/size, and overlay span already
  agree on `handleRayShieldedNpcDestroy` — confirm only.
- H2: generated code still carries placeholder `func_800E4070` (or a
  stale alias) and needs a TOML + fixup rename, or TOML is still
  `func_800E4070` while generated/overlay already use the human name.
- H3: overlay collision, a leftover splat disagreement, or size/boundary
  disagreement with the companion listing (expected size `0x40C`:
  `0x800E447C - 0x800E4070`, between leftover `fake_func_800E406C` and
  leftover `fake_func_800E447C`).
- H4: companion, generated body, TOML, or section-4 row is missing.

Exact commands (read-only census; no game run):

```
# companion
grep -n 'handleRayShieldedNpcDestroy\|func_800E4070\|800E4070\|E4070' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/*.txt
# generated
grep -n 'handleRayShieldedNpcDestroy\|func_800E4070\|0x800E4070' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_39.c
# toml + overlay inl
grep -n '800E4070\|handleRayShieldedNpcDestroy\|func_800E4070' \
  syms/rogue_squadron.syms.toml \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl
```

Expected splits:

- H1: all four sources already say `handleRayShieldedNpcDestroy`, size
  `0x40C`, previous leftover `fake_func_800E406C` / `0x800E406C`, next
  leftover `fake_func_800E447C` / `0x800E447C`, no leftover
  `func_800E4070` placeholder.
- H2: generated still `func_800E4070`, or TOML disagrees with
  generated/overlay — rename in TOML and the fixup path.
- H3: menu/cinematic occupant, a leftover splat at this address, or
  size != `0x40C`.
- H4: a required source is absent.

Do not reopen the attract-1024 six-entry, jump-table, or s1776
main-text 11-PC recipes. Next retail-entry revisit (when last-15 are
all sweep again) watches `submitGfxFrame` callers for the extra +105.
