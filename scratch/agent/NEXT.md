# NEXT work unit (s1649)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Run one bounded exact-name census for `func_800C7884`, independently named
`setHudFlagBit40AndStoreArg` at `0x800C7884` (size `0x1C`). Record the address,
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
`setHudFlagBit40AndStoreArg` mapping plus a live generated body and exact
`0x800C7864` / `0x800C78A0` boundaries select H1; ownership conflict selects
H2; no name, any conflict, or non-function evidence selects H3.

Before the census, run:

```sh
grep -n '^## Session ' PORTING-STATE.md | tail -15
```

Then run these bounded commands:

```sh
rg -n -C 8 '800C7884|setHudFlagBit40AndStoreArg' ../rogue_squadron64/symbol_files/mission_overlay.txt
rg -n -C 12 '800C7864|800C7884|800C78A0|setHudFlagBit40AndStoreArg' ../N64Recomp/RecompiledFuncs/funcs_36.c
rg -n -C 3 '800C7864|800C7884|800C78A0' syms/rogue_squadron.syms.toml
rg -n -C 3 '800C7864|800C7884|800C78A0|setHudFlagBit40AndStoreArg' ../N64Recomp/RecompiledFuncs/recomp_overlays.inl
rg -n -C 10 'setHudFlagBit40AndStoreArg' ../rogue_squadron64 --glob '*.c' --glob '*.h' --glob '*.inc.c' --glob '*.txt' | head -240
```
