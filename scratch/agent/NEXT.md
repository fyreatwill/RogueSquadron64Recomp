# NEXT work unit (s1644)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Run one bounded exact-name census for `func_800C776C`, independently named
`setHudEnableBit8` at `0x800C776C` (size `0x34`). Record the address, size,
generated definition/body, companion references and semantic comment, TOML
entry, section-4 overlay span, and previous/next boundaries before editing.
Synchronize the stale project name only if all independent evidence agrees.
Do not build or run.

Competing hypotheses and discriminator:

- H1: the companion mission name is owned by this entry, the generated body
  is live, and generated/TOML/overlay boundaries and size agree; synchronize.
- H2: the matching name belongs to another overlay or context; leave the
  address-coded mission entry unchanged.
- H3: no independent name is available, a span/size/boundary conflicts, or
  the entry is data-like; leave it parked.

The complete comparison table selects exactly one outcome: independent
`setHudEnableBit8` mapping plus a live generated body and exact
`getObjectiveGlobalFloat` / `0x800C77A0` boundaries select H1; ownership
conflict selects H2; no name, any conflict, or non-function evidence selects
H3.

Before the census, run:

```sh
grep -n '^## Session ' PORTING-STATE.md | tail -15
```

Then run these bounded commands:

```sh
rg -n -C 8 '800C776C|setHudEnableBit8' ../rogue_squadron64/symbol_files/mission_overlay.txt
rg -n -C 12 '800C7738|800C776C|800C77A0|setHudEnableBit8' ../N64Recomp/RecompiledFuncs/funcs_35.c
rg -n -C 3 '800C7738|800C776C|800C77A0' syms/rogue_squadron.syms.toml
rg -n -C 3 '800C7738|800C776C|800C77A0|setHudEnableBit8' ../N64Recomp/RecompiledFuncs/recomp_overlays.inl
```
