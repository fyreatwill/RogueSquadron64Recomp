# s2907 generated-symbol interval table

Interval: `0x80040304..0x80040308` in `main_overlay`.

| Address | Generated body | Companion/source evidence | Generated callers/lookups | Action |
|---|---|---|---|---|
| `0x80040304` | 12-byte generated `__builtin_trap()`; fixup report says the original decoded body had missing target label `L_80040314` | Companion map had only `fake_func_80040304`; no m2c/source function or semantic name. It is bounded between `destroyTransientNpcSlots` ending at `0x80040304` and `allocAndInitParticlePool` beginning at `0x80040310` | No generated calls or address lookups; only the overlay metadata entry | Rename to `data_gap_80040304` |

## Discriminator

`H-CallableSemantic` is not supported: no companion semantic name or source
body exists. `H-DataGap` is selected: the record is a fixup trap for a
12-byte interval between established callable bodies, with no generated
callers or lookups. `H-Ambiguous` remains the rejected alternative because
an external indirect entry cannot be disproved from generated references
alone, but there is no positive callable evidence.

The regeneration-safe mapping, companion map, project symbol map, generated
C/header, and overlay metadata were synchronized. Exact old-name searches
returned zero results after the rename.
