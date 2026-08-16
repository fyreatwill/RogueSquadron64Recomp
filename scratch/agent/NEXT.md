# NEXT work unit (s1718)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the census at `npcTankDroidComputeAimMotion` / `func_800D634C` at
`0x800D634C` (size `0x64C`). Last-15 titles after s1717 still include
the s1714 retail-entry revisit, so the mandatory REVISIT gate does not
fire.

s1717 synchronized `npcTickEffectChannelShared` at `0x800D6134` (size
`0x218`); generated headers/body and the section-4 row were already
named, and only the TOML placeholder was stale.

Competing hypotheses and discriminator:

- H1: already fully synchronized (companion, generated body, TOML name
  and size, section-4 span, adjacent boundaries all already agree).
- H2: companion mapping, live generated body, adjacent boundaries,
  TOML size, and section-4 span agree, but TOML and/or generated
  headers still carry `func_800D634C` — synchronize the name.
- H3: overlay collision, fake fragment, or size/boundary disagreement
  — classify the occupant and do not force the companion name.
- H4: companion, generated body, TOML, or section-4 row is missing, or
  the body has no readable semantics — leave as `func_*`.

```sh
# companion name, neighbors, overlay occupancy
grep -n 'npcTankDroidComputeAimMotion\|800D634C\|func_800D634C' \
  ~/Documents/Tools/rogue_squadron64/symbol_files/*
# generated body + headers
grep -n 'npcTankDroidComputeAimMotion\|func_800D634C\|0x800D634C' \
  ../N64Recomp/RecompiledFuncs/funcs.h \
  ../N64Recomp/RecompiledFuncs/funcs_38.c
# TOML + overlay span
grep -n '800D634C\|npcTankDroidComputeAimMotion' \
  syms/rogue_squadron.syms.toml \
  ../N64Recomp/RecompiledFuncs/recomp_overlays.inl
```

Expected splits:

- H1: no source-map edit; confirm only.
- H2: rename TOML and/or generated headers/body to
  `npcTankDroidComputeAimMotion`; size stays `0x64C`.
- H3: document the collision or fragment; next candidate is the
  following contiguous mission function.
- H4: leave the placeholder; write why semantics are unread.

Next contiguous candidate after this address is whatever the generated
and companion neighbors name past `0x800D634C + 0x64C = 0x800D6998`
(`npcTankDroidUpdate`).
