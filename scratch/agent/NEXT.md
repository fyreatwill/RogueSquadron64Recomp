# NEXT work unit (s1745)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the generated-symbol census at `npcRadarDishInit` /
`func_800DC228` (`0x800DC228`, size `0xD8`). s1744 closed the mandatory
15-title REVISIT (H3-stop-tick on the attract 1024). Last-15 after this
commit will include s1744, so the revisit gate does not fire.

Competing hypotheses:

- H1: companion `npcRadarDishInit`, generated body, TOML name/size, and
  overlay span already agree — confirm only.
- H2: generated code still carries placeholder `func_800DC228` (or a
  stale alias) and needs a TOML + fixup rename.
- H3: overlay collision, leftover `fake_func_*`, or size/boundary
  disagreement with the companion listing.
- H4: companion, generated body, TOML, or section-4 row is missing.

Exact commands (read-only census; no game run):

```
# companion
grep -n 'npcRadarDish\|800DC228\|DC228' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/*.txt
# generated
grep -n 'npcRadarDishInit\|func_800DC228\|0x800DC228' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_38.c
# toml + overlay inl
grep -n '800DC228\|npcRadarDishInit' \
  syms/rogue_squadron.syms.toml RecompiledFuncs/recomp_overlays.inl
```

Expected splits:

- H1: all four sources already say `npcRadarDishInit`, size `0xD8`,
  previous `npcTieVariantUpdate` / `0x800DB11C`, no leftover placeholder.
- H2: generated still `func_800DC228` — rename in TOML and the fixup path.
- H3: menu/cinematic occupant, leftover splat, or size != `0xD8`.
- H4: a required source is absent.

Do not reopen the attract-1024 six-entry recipe. Next cursor after this
address is whatever the census names as the following mission function.
