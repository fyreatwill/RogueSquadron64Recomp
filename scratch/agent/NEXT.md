# NEXT work unit (s1785)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the generated-symbol census at `playDualTextureAttachmentCueC`
(`0x800E49B4`, size `0x1FC`). s1776 was the last mandatory REVISIT
(`selected H1 submitGfxFrame on the attract 1024`); last-15 titles
after s1784 include that revisit, so the all-sweep REVISIT gate
does not fire. Neighbor peek: companion, generated headers/body, and
section-4 already use the human name; TOML is still `func_800E49B4`.

Competing hypotheses:

- H1: companion, generated body, TOML name/size, and overlay span already
  agree on `playDualTextureAttachmentCueC` — confirm only.
- H2: generated code still carries placeholder `func_800E49B4` (or a
  stale alias) and needs a TOML + fixup rename, or TOML disagrees with
  generated/overlay (expected: TOML still `func_800E49B4`).
- H3: overlay collision, a leftover splat disagreement, or size/boundary
  disagreement with the companion listing (expected size `0x1FC`:
  `0x800E4BB0 - 0x800E49B4`, between `playAttachmentMaterialSoundSimpleB`
  and `transformCraftAnchorsApplySubFx2` / leftover `func_800E4BB0`).
- H4: companion, generated body, TOML, or section-4 row is missing.

Exact commands (read-only census; no game run):

```
# companion
grep -n 'playDualTextureAttachmentCueC\|func_800E49B4\|800E49B4\|E49B4' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/*.txt
# generated
grep -n 'playDualTextureAttachmentCueC\|func_800E49B4\|0x800E49B4' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_39.c
# toml + overlay inl
grep -n '800E49B4\|playDualTextureAttachmentCueC\|func_800E49B4' \
  syms/rogue_squadron.syms.toml \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl
```

Expected splits:

- H1: all four sources already say `playDualTextureAttachmentCueC`, size
  `0x1FC`, previous `playAttachmentMaterialSoundSimpleB` / `0x800E4874`,
  next `transformCraftAnchorsApplySubFx2` / leftover `func_800E4BB0` /
  `0x800E4BB0`, no leftover `func_800E49B4` placeholder.
- H2: generated still `func_800E49B4`, or TOML disagrees with
  generated/overlay — rename in TOML and the fixup path.
- H3: menu/cinematic occupant, a leftover splat at this address, or
  size != `0x1FC`.
- H4: a required source is absent.

Do not reopen the attract-1024 six-entry, jump-table, or s1776
main-text 11-PC recipes. Next retail-entry revisit (when last-15 are
all sweep again) watches `submitGfxFrame` callers for the extra +105.
