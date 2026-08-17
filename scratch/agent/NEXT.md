# NEXT work unit (s1768)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the generated-symbol census at `transformCraftAnchorsAndApplySubFx`
/ `func_800E08F8` (`0x800E08F8`, size `0x3EC`). s1767 synchronized
`playAttachmentMaterialSoundSimple`; neighbor peek already shows TOML
still `func_800E08F8` while generated/overlay use the human name. Last-15
titles after s1767 still include s1760's revisit, so the all-sweep
15→REVISIT gate does not fire.

Competing hypotheses:

- H1: companion, generated body, TOML name/size, and overlay span already
  agree on `transformCraftAnchorsAndApplySubFx` — confirm only.
- H2: generated code still carries placeholder `func_800E08F8` (or a
  stale alias) and needs a TOML + fixup rename, or TOML is still
  `func_800E08F8` while generated/overlay already use the human name.
  Neighbor peek from s1767 already saw this TOML/overlay split — confirm
  it on the live body before renaming.
- H3: overlay collision, a leftover splat, or size/boundary disagreement
  with the companion listing.
- H4: companion, generated body, TOML, or section-4 row is missing.

Exact commands (read-only census; no game run):

```
# companion
grep -n 'transformCraftAnchorsAndApplySubFx\|func_800E08F8\|800E08F8\|E08F8' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/*.txt
# generated
grep -n 'transformCraftAnchorsAndApplySubFx\|func_800E08F8\|0x800E08F8' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_39.c
# toml + overlay inl
grep -n '800E08F8\|transformCraftAnchorsAndApplySubFx\|func_800E08F8' \
  syms/rogue_squadron.syms.toml \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl
```

Expected splits:

- H1: all four sources already say `transformCraftAnchorsAndApplySubFx`,
  size `0x3EC`, previous `playAttachmentMaterialSoundSimple` /
  `0x800E0748`, next `tickCraftSplineOrientation` /
  `0x800E0CE4`, no leftover `func_800E08F8` placeholder.
- H2: generated still `func_800E08F8`, or TOML still `func_800E08F8`
  while generated/overlay already use the human name — rename in TOML
  and the fixup path.
- H3: menu/cinematic occupant, a leftover splat at this address, or
  size != `0x3EC`.
- H4: a required source is absent.

Do not reopen the attract-1024 six-entry or jump-table recipes. Next
cursor after this address is `tickCraftSplineOrientation`
(`0x800E0CE4`).
