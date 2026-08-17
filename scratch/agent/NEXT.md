# NEXT work unit (s1778)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the generated-symbol census at `playDualTextureAttachmentCueMode1`
/ `func_800E4050` (`0x800E4050`, size `0x1C`). s1776 was the last
mandatory REVISIT (`selected H1 submitGfxFrame on the attract 1024`);
last-15 titles after s1777 include that revisit, so the all-sweep
15→REVISIT gate does not fire. Neighbor peek: TOML still
`func_800E4050` while generated/overlay already use the human name.

Competing hypotheses:

- H1: companion, generated body, TOML name/size, and overlay span already
  agree on `playDualTextureAttachmentCueMode1` — confirm only.
- H2: generated code still carries placeholder `func_800E4050` (or a
  stale alias) and needs a TOML + fixup rename, or TOML is still
  `func_800E4050` while generated/overlay already use the human name.
  Neighbor peek from s1777 already saw the TOML placeholder — confirm
  it on the live body before treating this as H2.
- H3: overlay collision, a leftover splat, or size/boundary disagreement
  with the companion listing.
- H4: companion, generated body, TOML, or section-4 row is missing.

Exact commands (read-only census; no game run):

```
# companion
grep -n 'playDualTextureAttachmentCueMode1\|func_800E4050\|800E4050\|E4050' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/*.txt
# generated
grep -n 'playDualTextureAttachmentCueMode1\|func_800E4050\|0x800E4050' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_39.c
# toml + overlay inl
grep -n '800E4050\|playDualTextureAttachmentCueMode1\|func_800E4050' \
  syms/rogue_squadron.syms.toml \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl
```

Expected splits:

- H1: all four sources already say `playDualTextureAttachmentCueMode1`,
  size `0x1C`, previous `playDualTextureAttachmentCueMode0` / `0x800E4034`,
  no leftover `func_800E4050` placeholder.
- H2: generated still `func_800E4050`, or TOML still `func_800E4050`
  while generated/overlay already use the human name — rename in TOML
  and the fixup path.
- H3: menu/cinematic occupant, a leftover splat at this address, or
  size != `0x1C`.
- H4: a required source is absent.

Do not reopen the attract-1024 six-entry, jump-table, or s1776
main-text 11-PC recipes. Next retail-entry revisit (when last-15 are
all sweep again) watches `submitGfxFrame` callers for the extra +105.
