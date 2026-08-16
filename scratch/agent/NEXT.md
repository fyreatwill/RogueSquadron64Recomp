# NEXT work unit (s1621)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the bounded generated-symbol sweep with one exact-name census over
`0x800C4D8C..0x800C51E0`. Record the address, size, generated definition/body,
companion references, and previous/next boundaries before editing. Synchronize
the name only if an independent mission-overlay name and the generated,
TOML, and overlay spans agree. Do not build or run.

Competing hypotheses and discriminator:

- H1: `func_800C4D8C` has the independently supported mission-overlay name
  `updateCraftSelectAnimState`, and its live generated body plus exact span
  support synchronization.
- H2: the companion project has no independent semantic name for this entry,
  so the address-encoded placeholder remains the least-assumptive label.
- H3: the name belongs to another overlay/context, or the generated, TOML,
  and overlay boundaries conflict or the entry is data-like, so it stays
  parked.

The complete comparison table is the discriminator: an independent mission
name plus a live generated body, matching `0x454` TOML/overlay span, and exact
preceding `initializeRadar` and following `placeRadarDots` boundaries select
H1; no independent mission name with otherwise coherent boundaries selects
H2; another-overlay ownership, any span conflict, or non-function evidence
selects H3. Each outcome selects one hypothesis.

Before starting the census, run:

```sh
grep -n '^## Session ' PORTING-STATE.md | tail -15
```

Use these bounded commands:

```sh
rg -n -C 8 '800C4D8C|updateCraftSelectAnimState' ../rogue_squadron64
rg -n -C 12 '800C4D8C|800C51E0' ../N64Recomp/RecompiledFuncs/funcs_34.c
rg -n -C 3 '800C4D8C|800C51E0' syms/rogue_squadron.syms.toml
rg -n -C 3 'updateCraftSelectAnimState|func_800C4D8C|800C51E0' ../N64Recomp/RecompiledFuncs/recomp_overlays.inl
```
