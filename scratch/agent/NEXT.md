# NEXT work unit (s1639)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Run one bounded exact-name census for `func_800C7358`, the mission-overlay
entry independently named `checkComplexObjectives` at `0x800C7358` (size
`0x38`). Record the address, size, generated definition/body, companion
references, TOML entry, overlay span, and previous/next boundaries before
editing. Synchronize the stale name only if all independent evidence agrees.
This is a documentation/source-map change; do not build or run.

Competing hypotheses and discriminator:

- H1: the companion mission name is owned by this entry, the generated body
  is live, and generated/TOML/overlay boundaries and size agree; synchronize.
- H2: the matching name belongs to another overlay or context; leave the
  mission placeholder address-coded.
- H3: no independent name is available, a span/size/boundary conflicts, or
  the entry is data-like; leave it parked.

The complete comparison table selects exactly one outcome: independent name
plus live body and exact `calculateFriendliesSaved` / `dealDamagetoDatItem`
boundaries selects H1; ownership conflict selects H2; no name, any conflict,
or non-function evidence selects H3.

Before the census, run:

```sh
grep -n '^## Session ' PORTING-STATE.md | tail -15
```

Then run these bounded commands:

```sh
rg -n -C 8 '800C7358|800C7390|checkComplexObjectives' ../rogue_squadron64
rg -n -C 12 '800C7358|800C7390' ../N64Recomp/RecompiledFuncs/funcs_35.c
rg -n -C 3 '800C7358|800C7390' syms/rogue_squadron.syms.toml
rg -n -C 3 '800C7358|800C7390|checkComplexObjectives' ../N64Recomp/RecompiledFuncs/recomp_overlays.inl
```
