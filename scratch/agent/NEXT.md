# NEXT work unit (s1733)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the census at `npcWingmanState2` at `0x800D9F90`
(size `0xD4`). s1732 confirmed `npcWingmanUpdate`.
Last-15 titles after s1732 still include the s1728 maintenance
compaction, so the mandatory REVISIT gate does not fire.

Competing hypotheses and discriminator:

- H1: already fully synchronized (companion, generated body, TOML name
  and size, section-4 span, adjacent boundaries all already agree).
- H2: companion mapping, live generated body, adjacent boundaries,
  TOML size, and section-4 span agree, but TOML and/or generated
  headers still carry `func_800D9F90` — synchronize the name.
- H3: overlay collision, fake fragment, or size/boundary disagreement
  — classify the occupant and do not force the companion name.
- H4: companion, generated body, TOML, or section-4 row is missing, or
  the body has no readable semantics — leave as `func_*`.

```sh
# companion name, neighbors, overlay occupancy
grep -n 'npcWingmanState2\|800D9F90\|func_800D9F90' \
  ~/Documents/Tools/rogue_squadron64/symbol_files/*
# generated body + headers
grep -n 'npcWingmanState2\|func_800D9F90\|0x800D9F90' \
  ../N64Recomp/RecompiledFuncs/funcs.h \
  ../N64Recomp/RecompiledFuncs/funcs_38.c
# TOML + overlay span
grep -n '800D9F90\|npcWingmanState2' \
  syms/rogue_squadron.syms.toml \
  ../N64Recomp/RecompiledFuncs/recomp_overlays.inl
```

Expected splits:

- H1: no source-map edit; confirm only.
- H2: rename TOML and/or generated headers/body to
  `npcWingmanState2`; size stays `0xD4`.
- H3: document the collision or fragment; next candidate is the
  following contiguous mission function.
- H4: leave the placeholder; write why semantics are unread.

Next contiguous candidate after this address is whatever the generated
and companion neighbors name past `0x800D9F90 + 0xD4 = 0x800DA064`
(`npcWingmanState3` / `func_800DA064`).
