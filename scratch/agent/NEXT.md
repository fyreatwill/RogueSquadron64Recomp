# NEXT work unit (s1756)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the generated-symbol census at `npcGroundTransportPlayFriendlyFireWarn`
/ `func_800DE4EC` / `0x800DE4EC` (size `0x320`). s1755 synchronized
`tickEnemyCraftWithDestruction`. Last-15 after this commit still
include s1744's revisit, so the mandatory REVISIT gate does not fire.

Competing hypotheses:

- H1: companion `npcGroundTransportPlayFriendlyFireWarn`, generated body, TOML
  name/size, and overlay span already agree — confirm only.
- H2: generated code still carries placeholder `func_800DE4EC` (or a
  stale alias) and needs a TOML + fixup rename.
- H3: overlay collision, leftover `fake_func_*`, or size/boundary
  disagreement with the companion listing.
- H4: companion, generated body, TOML, or section-4 row is missing.

Exact commands (read-only census; no game run):

```
# companion
grep -n 'npcGroundTransportPlayFriendlyFireWarn\|800DE4EC\|DE4EC' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/*.txt
# generated
grep -n 'npcGroundTransportPlayFriendlyFireWarn\|func_800DE4EC\|0x800DE4EC' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_38.c
# toml + overlay inl
grep -n '800DE4EC\|npcGroundTransportPlayFriendlyFireWarn' \
  syms/rogue_squadron.syms.toml \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl
```

Expected splits:

- H1: all four sources already say `npcGroundTransportPlayFriendlyFireWarn`,
  size `0x320`, previous `tickEnemyCraftWithDestruction` /
  `0x800DDBF0`, next `npcGroundTransportUpdate` / `0x800DE80C`,
  no leftover placeholder.
- H2: generated still `func_800DE4EC`, or TOML still `func_800DE4EC`
  while generated/overlay already use the human name — rename in TOML
  and the fixup path.
- H3: menu/cinematic occupant, leftover splat, or size != `0x320`.
- H4: a required source is absent.

Do not reopen the attract-1024 six-entry recipe. Next cursor after this
address is whatever the census names as the following mission function.
