# NEXT work unit (s1618)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Run exactly one bounded exact-name census over `0x800C41B0..0x800C435C`.
Record the address, size, generated definition/body, companion references, and
the previous/next boundaries before editing. Synchronize a name only if an
independent mission-overlay name and the generated/TOML/overlay span agree.
Do not build or run.

Competing hypotheses and discriminator:

- H1: `func_800C41B0` has an independently supported mission-overlay semantic
  name, and its live generated body plus exact span support synchronization.
- H2: the companion project has no independent semantic name for this entry,
  so the address-encoded placeholder remains the least-assumptive label.
- H3: a name is present only in another overlay/context, or the generated,
  TOML, and overlay boundaries conflict or are data-like, so the entry stays
  parked pending correction.

The complete comparison table is the discriminator: an independent
mission-overlay name plus a live generated body, matching `0x1AC`
TOML/overlay span, and exact preceding `fake_func_800C41AC` and following
`func_800C435C` boundaries select H1; no independent mission name with
otherwise coherent boundaries selects H2; another-overlay ownership, any span
conflict, or non-function evidence selects H3. Each outcome selects one
hypothesis.

Before starting the census, run:

```
grep -n '^## Session ' PORTING-STATE.md | tail -15
```

The last title is s1616's retail-entry revisit, so the mandatory every-15
sessions rule permits this sweep census. Use these bounded commands:

```
rg -n -C 8 '800C41B0|func_800C41B0' ../rogue_squadron64
rg -n -C 12 '800C41B0|800C435C' ../N64Recomp/RecompiledFuncs/funcs_33.c
rg -n -C 3 '800C41B0|800C435C' syms/rogue_squadron.syms.toml
rg -n -C 3 'func_800C41B0|func_800C435C' ../N64Recomp/RecompiledFuncs/recomp_overlays.inl
```
