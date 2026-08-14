# NEXT work unit (s1082)

HYPOTHESIS-ID: oracle-512-state-gate-owner

Run exactly one bounded static census of every generated and companion write
that can alias `0x80130B30` after `runIdleFramesAndLoadSaveData` returns and
before the `mainGameLoop` gate at `0x8003E07C`. Do not build, run the oracle,
change the input schedule, or arm a freelist watch.

Competing hypotheses and discriminator:

* `H-no-later-clobber`: no concrete post-return write aliases the byte, so a
  runtime zero requires an execution/overlay boundary.
* `H-later-clobber`: a concrete write can reset or replace the byte before the
  gate.
* `H-raw-open`: only unresolved raw/indirect bases remain, so static coverage
  cannot classify the value.

Discriminating measurement: a complete post-return write table with no
concrete alias selects `H-no-later-clobber`; a concrete alias selects
`H-later-clobber`; only unresolved raw/indirect candidates select
`H-raw-open`.
Before any build, run:

```sh
rg -n -S '80130B30|D_80130B10|MEM_B\(0X20|MEM_B\(0x20' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs patches src docs scratch tools --glob '*.{c,h,cpp,md,txt,sh}'
rg -n -S '80130B30|D_80130B10|0x80130B30' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64 --glob '*.{c,h,txt,s}'
```
