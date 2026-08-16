# NEXT work unit (s1634)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the bounded generated-symbol sweep with one exact-name census of
`func_800C722C`, the `0x800C722C..0x800C723C` entry independently named
`getConfigFloatValue`. Record the address, size, generated definition/body,
companion references, and previous/next boundaries before editing.
Synchronize the name only if an independent mission-overlay name and the
generated, TOML, and overlay spans agree. Do not build or run.

Competing hypotheses and discriminator:

- H1: `func_800C722C` has an independently supported mission-overlay name,
  and its live generated body plus exact span support synchronization.
- H2: the only matching name belongs to another overlay/context, so the
  mission-overlay placeholder must remain address-coded despite a live body.
- H3: no independent name is available, or the generated, TOML, or overlay
  boundaries conflict, or the entry is data-like, so it stays parked.

The complete comparison table is the discriminator: an independent mission
name plus a live generated body, matching TOML/overlay span, and exact
preceding `accumulateVectorInObjectFrame` and following `func_800C723C`
boundaries select H1; an ownership conflict selects H2; no independent name,
any span conflict, or non-function evidence selects H3. Each outcome selects
one hypothesis.

Before starting the census, run:

```sh
grep -n '^## Session ' PORTING-STATE.md | tail -15
```

Use these bounded commands:

```sh
rg -n -C 8 '800C722C|800C723C|getConfigFloatValue' ../rogue_squadron64
rg -n -C 12 '800C722C|800C723C|getConfigFloatValue' ../N64Recomp/RecompiledFuncs/funcs_35.c
rg -n -C 3 '800C722C|800C723C' syms/rogue_squadron.syms.toml
rg -n -C 3 '800C722C|800C723C|getConfigFloatValue' ../N64Recomp/RecompiledFuncs/recomp_overlays.inl
```
