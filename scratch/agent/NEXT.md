# NEXT work unit (s1715)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the census at `npcDebrisFieldUpdate` / `func_800D5208` at
`0x800D5208` (size `0xDD8`). Last-15 titles after s1714 still include
the s1714 retail-entry revisit, so the mandatory REVISIT gate does not
fire.

s1714 classified attract-512 A/Start/C-up/L/Z as the same title-like
`512→1024` at 126.3–126.4 s that stays 1024 through 133.5 s. Do not
repeat that 133 s recipe.

Competing hypotheses and discriminator:

- H1: already fully synchronized (companion, generated body, TOML name
  and size, section-4 span, adjacent boundaries all already agree).
- H2: companion mapping, live generated body, adjacent boundaries,
  TOML size, and section-4 span agree, but TOML and/or generated
  headers still carry `func_800D5208` — synchronize the name.
- H3: overlay collision, fake fragment, or size/boundary disagreement
  — classify the occupant and do not force the companion name.
- H4: companion, generated body, TOML, or section-4 row is missing, or
  the body has no readable semantics — leave as `func_*`.

```sh
# companion name, neighbors, overlay occupancy
rg -n 'npcDebrisFieldUpdate|800D5208|func_800D5208' \
  ~/Documents/Tools/rogue_squadron64
# generated body + headers
rg -n 'npcDebrisFieldUpdate|func_800D5208|0x800D5208' \
  RecompiledFuncs/ funcs.h
# TOML + overlay span
rg -n '800D5208|npcDebrisFieldUpdate' \
  syms/rogue_squadron.syms.toml RecompiledFuncs/recomp_overlays.inl
```

Expected splits:

- H1: no source-map edit; confirm only.
- H2: rename TOML and/or generated headers/body to
  `npcDebrisFieldUpdate`; size stays `0xDD8`.
- H3: document the collision or fragment; next candidate is the
  following contiguous mission function.
- H4: leave the placeholder; write why semantics are unread.

Next contiguous candidate after this address is whatever the generated
and companion neighbors name past `0x800D5208 + 0xDD8 = 0x800D5FE0`.
