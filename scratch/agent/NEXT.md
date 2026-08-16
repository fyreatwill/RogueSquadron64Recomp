# NEXT work unit (s1729)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the census at `npcWingmanSpawnBurstEffects` at `0x800D8988`
(size `0x330`). s1728 was a triggered maintenance compaction (no
sweep step). Last-15 titles after s1728 still include the s1714
retail-entry revisit, so the mandatory REVISIT gate does not fire.

Competing hypotheses and discriminator:

- H1: already fully synchronized (companion, generated body, TOML name
  and size, section-4 span, adjacent boundaries all already agree).
- H2: companion mapping, live generated body, adjacent boundaries,
  TOML size, and section-4 span agree, but TOML and/or generated
  headers still carry `func_800D8988` — synchronize the name.
- H3: overlay collision, fake fragment, or size/boundary disagreement
  — classify the occupant and do not force the companion name.
- H4: companion, generated body, TOML, or section-4 row is missing, or
  the body has no readable semantics — leave as `func_*`.

```sh
# companion name, neighbors, overlay occupancy
grep -n 'npcWingmanSpawnBurstEffects\|800D8988\|func_800D8988' \
  ~/Documents/Tools/rogue_squadron64/symbol_files/*
# generated body + headers
grep -n 'npcWingmanSpawnBurstEffects\|func_800D8988\|0x800D8988' \
  ../N64Recomp/RecompiledFuncs/funcs.h \
  ../N64Recomp/RecompiledFuncs/funcs_38.c
# TOML + overlay span
grep -n '800D8988\|npcWingmanSpawnBurstEffects' \
  syms/rogue_squadron.syms.toml \
  ../N64Recomp/RecompiledFuncs/recomp_overlays.inl
```

Expected splits:

- H1: no source-map edit; confirm only.
- H2: rename TOML and/or generated headers/body to
  `npcWingmanSpawnBurstEffects`; size stays `0x330`.
- H3: document the collision or fragment; next candidate is the
  following contiguous mission function.
- H4: leave the placeholder; write why semantics are unread.

Next contiguous candidate after this address is whatever the generated
and companion neighbors name past `0x800D8988 + 0x330 = 0x800D8CB8`
(`func_800D8CB8` / `npcWingmanSteerToward`).
