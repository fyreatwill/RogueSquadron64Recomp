# NEXT work unit (s1721)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the census at `npcTickEffectChannelSharedMode1` at `0x800D7834`
(size `0x1C`). Last-15 titles after s1720 still include the s1714
retail-entry revisit, so the mandatory REVISIT gate does not fire.

s1720 synchronized `npcTickEffectChannelSharedMode0` at `0x800D7818`
(size `0x1C`): generated headers/body already used the companion name;
only the TOML placeholder was stale.

Competing hypotheses and discriminator:

- H1: already fully synchronized (companion, generated body, TOML name
  and size, section-4 span, adjacent boundaries all already agree).
- H2: companion mapping, live generated body, adjacent boundaries,
  TOML size, and section-4 span agree, but TOML and/or generated
  headers still carry `func_800D7834` — synchronize the name.
- H3: overlay collision, fake fragment, or size/boundary disagreement
  — classify the occupant and do not force the companion name.
- H4: companion, generated body, TOML, or section-4 row is missing, or
  the body has no readable semantics — leave as `func_*`.

```sh
# companion name, neighbors, overlay occupancy
grep -n 'npcTickEffectChannelSharedMode1\|800D7834\|func_800D7834' \
  ~/Documents/Tools/rogue_squadron64/symbol_files/*
# generated body + headers
grep -n 'npcTickEffectChannelSharedMode1\|func_800D7834\|0x800D7834' \
  ../N64Recomp/RecompiledFuncs/funcs.h \
  ../N64Recomp/RecompiledFuncs/funcs_38.c
# TOML + overlay span
grep -n '800D7834\|npcTickEffectChannelSharedMode1' \
  syms/rogue_squadron.syms.toml \
  ../N64Recomp/RecompiledFuncs/recomp_overlays.inl
```

Expected splits:

- H1: no source-map edit; confirm only.
- H2: rename TOML and/or generated headers/body to
  `npcTickEffectChannelSharedMode1`; size stays `0x1C`.
- H3: document the collision or fragment; next candidate is the
  following contiguous mission function.
- H4: leave the placeholder; write why semantics are unread.

Next contiguous candidate after this address is whatever the generated
and companion neighbors name past `0x800D7834 + 0x1C = 0x800D7850`
(`npcWingmanResetState` / `func_800D7850`).
