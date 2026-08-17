# NEXT work unit (s1782)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the generated-symbol census at `resetCraftInstanceMotionState`
(`0x800E4480`, size `0x1F4`). s1776 was the last mandatory REVISIT
(`selected H1 submitGfxFrame on the attract 1024`); last-15 titles
after s1781 include that revisit, so the all-sweep REVISIT gate does
not fire. Neighbor peek: companion, generated headers/body, and
section-4 already use the human name; TOML is still `func_800E4480`.
Companion deleted leftover `func_800E4480` at s432 as a duplicate of
this name.

Competing hypotheses:

- H1: companion, generated body, TOML name/size, and overlay span already
  agree on `resetCraftInstanceMotionState` — confirm only.
- H2: generated code still carries placeholder `func_800E4480` (or a
  stale alias) and needs a TOML + fixup rename, or TOML disagrees with
  generated/overlay (expected: TOML still `func_800E4480`).
- H3: overlay collision, a leftover splat disagreement, or size/boundary
  disagreement with the companion listing (expected size `0x1F4`:
  `0x800E4674 - 0x800E4480`, between leftover `fake_func_800E447C` and
  `playDualTextureAttachmentCueB` / leftover `func_800E4674`).
- H4: companion, generated body, TOML, or section-4 row is missing.

Exact commands (read-only census; no game run):

```
# companion
grep -n 'resetCraftInstanceMotionState\|func_800E4480\|800E4480\|E4480' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/*.txt
# generated
grep -n 'resetCraftInstanceMotionState\|func_800E4480\|0x800E4480' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_39.c
# toml + overlay inl
grep -n '800E4480\|resetCraftInstanceMotionState\|func_800E4480' \
  syms/rogue_squadron.syms.toml \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl
```

Expected splits:

- H1: all four sources already say `resetCraftInstanceMotionState`, size
  `0x1F4`, previous leftover `fake_func_800E447C` / `0x800E447C`, next
  `playDualTextureAttachmentCueB` / leftover `func_800E4674` /
  `0x800E4674`, no leftover `func_800E4480` placeholder.
- H2: generated still `func_800E4480`, or TOML disagrees with
  generated/overlay — rename in TOML and the fixup path.
- H3: menu/cinematic occupant, a leftover splat at this address, or
  size != `0x1F4`.
- H4: a required source is absent.

Do not reopen the attract-1024 six-entry, jump-table, or s1776
main-text 11-PC recipes. Next retail-entry revisit (when last-15 are
all sweep again) watches `submitGfxFrame` callers for the extra +105.
