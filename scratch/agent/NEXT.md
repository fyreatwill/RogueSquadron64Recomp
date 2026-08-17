# NEXT work unit (s1748)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the generated-symbol census at `npcInitMinimalNoAnim` /
`func_800DD248` / `0x800DD248` (size `0x7C`). s1747 confirmed
`npcRadarDishUpdate`. Last-15 after this commit still include
s1744's revisit, so the mandatory REVISIT gate does not fire.

Competing hypotheses:

- H1: companion `npcInitMinimalNoAnim`, generated body, TOML name/size,
  and overlay span already agree — confirm only.
- H2: generated code still carries placeholder `func_800DD248` (or a
  stale alias) and needs a TOML + fixup rename.
- H3: overlay collision, leftover `fake_func_*`, or size/boundary
  disagreement with the companion listing.
- H4: companion, generated body, TOML, or section-4 row is missing.

Exact commands (read-only census; no game run):

```
# companion
grep -n 'npcInitMinimalNoAnim\|800DD248\|DD248' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/*.txt
# generated
grep -n 'npcInitMinimalNoAnim\|func_800DD248\|0x800DD248' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_38.c
# toml + overlay inl
grep -n '800DD248\|npcInitMinimalNoAnim' \
  syms/rogue_squadron.syms.toml \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl
```

Expected splits:

- H1: all four sources already say `npcInitMinimalNoAnim`, size `0x7C`,
  previous `npcRadarDishUpdate` / `0x800DC6F0`, next
  `fake_func_800DD2C4` / `0x800DD2C4` then `npcInitFullModel` /
  `0x800DD2D0`, no leftover placeholder.
- H2: generated still `func_800DD248`, or TOML still `func_800DD248`
  while generated/overlay already use the human name — rename in TOML
  and the fixup path.
- H3: menu/cinematic occupant, leftover splat, or size != `0x7C`.
- H4: a required source is absent.

Do not reopen the attract-1024 six-entry recipe. Next cursor after this
address is whatever the census names as the following mission function.
