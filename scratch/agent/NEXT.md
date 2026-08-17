# NEXT work unit (s1753)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the generated-symbol census at `playAttachmentMaterialFadeSound` /
`func_800DD930` / `0x800DD930` (size `0x140`). s1752 synchronized
`npcTickEffectChannelE`. Last-15 after this commit still include
s1744's revisit, so the mandatory REVISIT gate does not fire.

Competing hypotheses:

- H1: companion `playAttachmentMaterialFadeSound`, generated body, TOML name/size,
  and overlay span already agree — confirm only.
- H2: generated code still carries placeholder `func_800DD930` (or a
  stale alias) and needs a TOML + fixup rename.
- H3: overlay collision, leftover `fake_func_*`, or size/boundary
  disagreement with the companion listing.
- H4: companion, generated body, TOML, or section-4 row is missing.

Exact commands (read-only census; no game run):

```
# companion
grep -n 'playAttachmentMaterialFadeSound\|800DD930\|DD930' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/*.txt
# generated
grep -n 'playAttachmentMaterialFadeSound\|func_800DD930\|0x800DD930' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_38.c
# toml + overlay inl
grep -n '800DD930\|playAttachmentMaterialFadeSound' \
  syms/rogue_squadron.syms.toml \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl
```

Expected splits:

- H1: all four sources already say `playAttachmentMaterialFadeSound`, size `0x140`,
  previous `npcTickEffectChannelE` / `0x800DD78C`, next
  `transformCraftDualAnchorsAndApplyMotion` / `0x800DDA70`, no leftover placeholder.
- H2: generated still `func_800DD930`, or TOML still `func_800DD930`
  while generated/overlay already use the human name — rename in TOML
  and the fixup path.
- H3: menu/cinematic occupant, leftover splat, or size != `0x140`.
- H4: a required source is absent.

Do not reopen the attract-1024 six-entry recipe. Next cursor after this
address is whatever the census names as the following mission function.
