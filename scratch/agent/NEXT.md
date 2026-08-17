# NEXT work unit (s1779)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the generated-symbol census at leftover `fake_func_800E406C`
(`0x800E406C`, size `0x4`). s1776 was the last mandatory REVISIT
(`selected H1 submitGfxFrame on the attract 1024`); last-15 titles
after s1778 include that revisit, so the all-sweep REVISIT gate does
not fire. Neighbor peek: companion, generated, TOML, and section-4
already use the leftover name.

Competing hypotheses:

- H1: companion, generated body, TOML name/size, and overlay span already
  agree on leftover `fake_func_800E406C` — confirm only.
- H2: generated code still carries placeholder `func_800E406C` (or a
  stale alias) and needs a TOML + fixup rename, or TOML is still
  `func_800E406C` while generated/overlay already use a different name.
- H3: overlay collision, a leftover splat disagreement, or size/boundary
  disagreement with the companion listing (expected size `0x4`: one
  `sw $a0, 0x20($sp)` between Mode1's epilogue and
  `handleRayShieldedNpcDestroy`'s prologue).
- H4: companion, generated body, TOML, or section-4 row is missing.

Exact commands (read-only census; no game run):

```
# companion
grep -n 'fake_func_800E406C\|func_800E406C\|800E406C\|E406C' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/*.txt
# generated
grep -n 'fake_func_800E406C\|func_800E406C\|0x800E406C' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_39.c
# toml + overlay inl
grep -n '800E406C\|fake_func_800E406C\|func_800E406C' \
  syms/rogue_squadron.syms.toml \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl
```

Expected splits:

- H1: all four sources already say `fake_func_800E406C`, size `0x4`,
  previous `playDualTextureAttachmentCueMode1` / `0x800E4050`, next
  `handleRayShieldedNpcDestroy` / `0x800E4070`, no leftover
  `func_800E406C` placeholder.
- H2: generated still `func_800E406C`, or TOML disagrees with
  generated/overlay — rename in TOML and the fixup path.
- H3: menu/cinematic occupant, a leftover splat at this address that is
  not the one-word `sw $a0` gap, or size != `0x4`.
- H4: a required source is absent.

Do not reopen the attract-1024 six-entry, jump-table, or s1776
main-text 11-PC recipes. Next retail-entry revisit (when last-15 are
all sweep again) watches `submitGfxFrame` callers for the extra +105.
