# NEXT work unit (s1762)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the generated-symbol census at `applyCraftAnimAndDetailParams`
/ `func_800DFB90` (`0x800DFB90`, size `0x3C4`). s1761 confirmed leftover
`fake_func_800DFB8C`. Last-15 titles after s1761 still include s1760's
revisit, so the all-sweep REVISIT gate does not fire.

Competing hypotheses:

- H1: companion, generated body, TOML name/size, and overlay span already
  agree on `applyCraftAnimAndDetailParams` — confirm only.
- H2: generated code still carries placeholder `func_800DFB90` (or a
  stale alias) and needs a TOML + fixup rename, or TOML is still
  `func_800DFB90` while generated/overlay already use the human name.
  Neighbor peek from s1761 already saw this TOML/overlay split — confirm
  it on the live body before renaming.
- H3: overlay collision, a leftover splat, or size/boundary disagreement
  with the companion listing. Companion deleted `func_800DFB90` at s432
  as a duplicate-symbol collision with this name.
- H4: companion, generated body, TOML, or section-4 row is missing.

Exact commands (read-only census; no game run):

```
# companion
grep -n 'applyCraftAnimAndDetailParams\|func_800DFB90\|800DFB90\|DFB90' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/*.txt
# generated
grep -n 'applyCraftAnimAndDetailParams\|func_800DFB90\|0x800DFB90' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_39.c
# toml + overlay inl
grep -n '800DFB90\|applyCraftAnimAndDetailParams\|func_800DFB90' \
  syms/rogue_squadron.syms.toml \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl
```

Expected splits:

- H1: all four sources already say `applyCraftAnimAndDetailParams`,
  size `0x3C4`, previous leftover `fake_func_800DFB8C` / `0x800DFB8C`,
  next `playAttachmentMaterialSoundVariantA` / `func_800DFF54` /
  `0x800DFF54`, no leftover `func_800DFB90` placeholder.
- H2: generated still `func_800DFB90`, or TOML still `func_800DFB90`
  while generated/overlay already use the human name — rename in TOML
  and the fixup path.
- H3: menu/cinematic occupant, a leftover splat at this address, or
  size != `0x3C4`.
- H4: a required source is absent.

Do not reopen the attract-1024 six-entry or jump-table recipes. Next
cursor after this address is `playAttachmentMaterialSoundVariantA` /
`func_800DFF54` (`0x800DFF54`, size `0x190`).
