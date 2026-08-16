# NEXT work unit (s1641)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Run one bounded exact-name census for `func_800C7718`, independently named
`getGlobalFloatGameState` at `0x800C7718` (size `0x10`). Record the address,
size, generated definition/body, companion references and semantic comment,
TOML entry, section-4 overlay span, and previous/next boundaries before
editing. Synchronize the stale project name only if all independent evidence
agrees. Do not build or run.

Competing hypotheses and discriminator:

- H1: the companion mission name is owned by this entry, the generated body
  is live, and generated/TOML/overlay boundaries and size agree; synchronize.
- H2: the matching name belongs to another overlay or context; leave the
  address-coded mission entry unchanged.
- H3: no independent name is available, a span/size/boundary conflicts, or
  the entry is data-like; leave it parked.

The complete comparison table selects exactly one outcome: independent
`getGlobalFloatGameState` mapping plus a live generated body and exact
`setObjectiveTimer` / `getObjectiveGlobalFloat` boundaries select H1;
ownership conflict selects H2; no name, any conflict, or non-function
evidence selects H3.

Before the census, run:

```sh
grep -n '^## Session ' PORTING-STATE.md | tail -15
```

Then run these bounded commands:

```sh
rg -n -C 8 '800C7718|getGlobalFloatGameState' ../rogue_squadron64/symbol_files/mission_overlay.txt
rg -n -C 12 '800C76FC|800C7718|800C7728|getGlobalFloatGameState' ../N64Recomp/RecompiledFuncs/funcs_35.c
rg -n -C 3 '800C76FC|800C7718|800C7728' syms/rogue_squadron.syms.toml
rg -n -C 3 '800C76FC|800C7718|800C7728|getGlobalFloatGameState' ../N64Recomp/RecompiledFuncs/recomp_overlays.inl
```
