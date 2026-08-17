# NEXT work unit (s1765)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the generated-symbol census at `playAttachmentCueWithSlotIter`
/ `func_800E026C` (`0x800E026C`, size `0x18C`). s1764 synchronized
`playAttachmentMaterialSoundVariantB`; neighbor peek already shows TOML
still `func_800E026C` while generated/overlay use the human name. Last-15
titles after s1764 still include s1760's revisit, so the all-sweep
REVISIT gate does not fire.

Competing hypotheses:

- H1: companion, generated body, TOML name/size, and overlay span already
  agree on `playAttachmentCueWithSlotIter` — confirm only.
- H2: generated code still carries placeholder `func_800E026C` (or a
  stale alias) and needs a TOML + fixup rename, or TOML is still
  `func_800E026C` while generated/overlay already use the human name.
  Neighbor peek from s1764 already saw this TOML/overlay split — confirm
  it on the live body before renaming.
- H3: overlay collision, a leftover splat, or size/boundary disagreement
  with the companion listing.
- H4: companion, generated body, TOML, or section-4 row is missing.

Exact commands (read-only census; no game run):

```
# companion
grep -n 'playAttachmentCueWithSlotIter\|func_800E026C\|800E026C\|E026C' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/*.txt
# generated
grep -n 'playAttachmentCueWithSlotIter\|func_800E026C\|0x800E026C' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_39.c
# toml + overlay inl
grep -n '800E026C\|playAttachmentCueWithSlotIter\|func_800E026C' \
  syms/rogue_squadron.syms.toml \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl
```

Expected splits:

- H1: all four sources already say `playAttachmentCueWithSlotIter`,
  size `0x18C`, previous `playAttachmentMaterialSoundVariantB` /
  `0x800E00E4`, next `playDualTextureAttachmentCue` / `func_800E03F8` /
  `0x800E03F8`, no leftover `func_800E026C` placeholder.
- H2: generated still `func_800E026C`, or TOML still `func_800E026C`
  while generated/overlay already use the human name — rename in TOML
  and the fixup path.
- H3: menu/cinematic occupant, a leftover splat at this address, or
  size != `0x18C`.
- H4: a required source is absent.

Do not reopen the attract-1024 six-entry or jump-table recipes. Next
cursor after this address is `playDualTextureAttachmentCue` /
`func_800E03F8` (`0x800E03F8`, size `0x350`).
