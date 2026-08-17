# NEXT work unit (s1746)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the generated-symbol census at `npcRadarDishComputeAimMotion` /
`func_800DC300` (`0x800DC300`, size `0x3F0`). s1745 synchronized
`npcRadarDishInit`. Last-15 after this commit still include s1744's
revisit, so the mandatory REVISIT gate does not fire.

Competing hypotheses:

- H1: companion `npcRadarDishComputeAimMotion`, generated body, TOML
  name/size, and overlay span already agree — confirm only.
- H2: generated code still carries placeholder `func_800DC300` (or a
  stale alias) and needs a TOML + fixup rename.
- H3: overlay collision, leftover `fake_func_*`, or size/boundary
  disagreement with the companion listing.
- H4: companion, generated body, TOML, or section-4 row is missing.

Exact commands (read-only census; no game run):

```
# companion
grep -n 'npcRadarDishComputeAimMotion\|800DC300\|DC300' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/*.txt
# generated
grep -n 'npcRadarDishComputeAimMotion\|func_800DC300\|0x800DC300' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_38.c
# toml + overlay inl
grep -n '800DC300\|npcRadarDishComputeAimMotion' \
  syms/rogue_squadron.syms.toml \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl
```

Expected splits:

- H1: all four sources already say `npcRadarDishComputeAimMotion`, size
  `0x3F0`, previous `npcRadarDishInit` / `0x800DC228`, no leftover
  placeholder.
- H2: generated still `func_800DC300` — rename in TOML and the fixup path.
- H3: menu/cinematic occupant, leftover splat, or size != `0x3F0`.
- H4: a required source is absent.

Do not reopen the attract-1024 six-entry recipe. Next cursor after this
address is whatever the census names as the following mission function.
