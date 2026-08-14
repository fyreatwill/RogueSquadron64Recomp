# NEXT work unit (s1081)

HYPOTHESIS-ID: oracle-512-state-gate-owner

Run exactly one bounded static audit of the `runIdleFramesAndLoadSaveData`
path surrounding writer `0x8006DAB8`. Enumerate all generated callers, any
early exits before the store of `1` to `0x80130B30`, and the reset-to-store
ordering before the width-320 attract loop. Do not build, run the oracle,
change the input schedule, or arm a freelist watch.

Competing hypotheses and discriminator:

* `H-writer-reached`: all callers reach the store after reset, so a runtime
  zero requires a later clobber or an execution/overlay boundary.
* `H-writer-skipped`: a caller or early-exit path can leave the byte at reset
  zero before the attract loop.
* `H-writer-open`: caller/ordering coverage remains incomplete.

Discriminating measurement: a complete caller/early-exit table with the store
on every pre-attract path selects `H-writer-reached`; a concrete path that
skips it selects `H-writer-skipped`; incomplete coverage selects
`H-writer-open`.
Before any build, run:

```sh
rg -n -S '8006DAB8|runIdleFramesAndLoadSaveData|resetGameSettingsAndMissionStats|80130B30' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs patches src docs scratch tools --glob '*.{c,h,cpp,md,txt,sh}'
rg -n -S '8006DAB8|runIdleFramesAndLoadSaveData|resetGameSettingsAndMissionStats|80130B30' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64 --glob '*.{c,h,txt,s}'
```
