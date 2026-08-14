# NEXT work unit (s1083)

HYPOTHESIS-ID: oracle-512-state-gate-owner

Run exactly one bounded static audit of `loadOverlay`'s DMA destination and
host overlay-loader writes after `runIdleFramesAndLoadSaveData` returns and
before the `mainGameLoop` gate at `0x8003E07C`. Do not build, run the oracle,
change the input schedule, or arm a freelist watch.

Competing hypotheses and discriminator:

* `H-loader-no-alias`: loader/DMA destinations exclude `0x80130B30`, so the
  static no-later-clobber result survives the opaque call.
* `H-loader-alias`: a loader/DMA write can touch the target byte before the
  gate.
* `H-loader-open`: the host/loader path is not statically traceable enough to
  classify its destination.

Discriminating measurement: the loader's concrete destination/range selects
`H-loader-no-alias` or `H-loader-alias`; an unresolved destination selects
`H-loader-open`.
Before any build, run:

```sh
rg -n -S '80130B30|D_80130B10|MEM_B\(0X20|MEM_B\(0x20' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs patches src docs scratch tools --glob '*.{c,h,cpp,md,txt,sh}'
rg -n -S '80130B30|D_80130B10|0x80130B30' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64 --glob '*.{c,h,txt,s}'
```

Then inspect only the bounded `loadOverlay` implementation, its DMA/host
helpers, and overlay destination symbols. Do not run a build or runtime probe.
