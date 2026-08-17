# NEXT work unit (s1783)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the generated-symbol census at `playDualTextureAttachmentCueB`
(`0x800E4674`, size `0x200`). s1776 was the last mandatory REVISIT
(`selected H1 submitGfxFrame on the attract 1024`); last-15 titles
after s1782 include that revisit, so the all-sweep REVISIT gate
does not fire. Neighbor peek: companion, generated headers/body, and
section-4 already use the human name; TOML is still `func_800E4674`.

Competing hypotheses:

- H1: companion, generated body, TOML name/size, and overlay span already
  agree on `playDualTextureAttachmentCueB` — confirm only.
- H2: generated code still carries placeholder `func_800E4674` (or a
  stale alias) and needs a TOML + fixup rename, or TOML disagrees with
  generated/overlay (expected: TOML still `func_800E4674`).
- H3: overlay collision, a leftover splat disagreement, or size/boundary
  disagreement with the companion listing (expected size `0x200`:
  `0x800E4874 - 0x800E4674`, between `resetCraftInstanceMotionState`
  and `playAttachmentMaterialSoundSimpleB` / leftover `func_800E4874`).
- H4: companion, generated body, TOML, or section-4 row is missing.

Exact commands (read-only census; no game run):

```
# companion
grep -n 'playDualTextureAttachmentCueB\|func_800E4674\|800E4674\|E4674' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/*.txt
# generated
grep -n 'playDualTextureAttachmentCueB\|func_800E4674\|0x800E4674' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_39.c
# toml + overlay inl
grep -n '800E4674\|playDualTextureAttachmentCueB\|func_800E4674' \
  syms/rogue_squadron.syms.toml \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl
```

Expected splits:

- H1: all four sources already say `playDualTextureAttachmentCueB`, size
  `0x200`, previous `resetCraftInstanceMotionState` / `0x800E4480`, next
  `playAttachmentMaterialSoundSimpleB` / leftover `func_800E4874` /
  `0x800E4874`, no leftover `func_800E4674` placeholder.
- H2: generated still `func_800E4674`, or TOML disagrees with
  generated/overlay — rename in TOML and the fixup path.
- H3: menu/cinematic occupant, a leftover splat at this address, or
  size != `0x200`.
- H4: a required source is absent.

Do not reopen the attract-1024 six-entry, jump-table, or s1776
main-text 11-PC recipes. Next retail-entry revisit (when last-15 are
all sweep again) watches `submitGfxFrame` callers for the extra +105.
