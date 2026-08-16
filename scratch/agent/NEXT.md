# NEXT work unit (s1627)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the bounded generated-symbol sweep with one exact-name census over
`0x800C6468..0x800C6498`. Record the address, size, generated definition/body,
companion references, and previous/next boundaries before editing. Synchronize
the name only if an independent mission-overlay name and the generated, TOML,
and overlay spans agree. Do not build or run.

Competing hypotheses and discriminator:

- H1: `func_800C6468` has the independently supported name
  `accumulateClampedFloatField`, and its live generated body plus exact
  span support synchronization.
- H2: `accumulateClampedFloatField` belongs to another overlay/context at
  this address, so the mission-overlay placeholder must remain address-coded
  despite a live body.
- H3: the generated, TOML, or overlay boundaries conflict, or the entry is
  data-like rather than a function, so it stays parked.

The complete comparison table is the discriminator: an independent mission
name plus a live generated clamped-float accumulation body, matching `0x30`
TOML/overlay span, and exact preceding `getAvailableShipsForLevel` and
following `getDisplayItemStateByte` boundaries select H1; an ownership
conflict selects H2; any span conflict or non-function evidence selects H3.
Each outcome selects one hypothesis.

Before starting the census, run:

```sh
grep -n '^## Session ' PORTING-STATE.md | tail -15
```

Use these bounded commands:

```sh
  rg -n -C 8 '800C6468|accumulateClampedFloatField' ../rogue_squadron64
  rg -n -C 12 '800C6468|800C6498' ../N64Recomp/RecompiledFuncs/funcs_34.c
  rg -n -C 3 '800C6468|800C6498' syms/rogue_squadron.syms.toml
  rg -n -C 3 'accumulateClampedFloatField|func_800C6468|800C6498' ../N64Recomp/RecompiledFuncs/recomp_overlays.inl
```
