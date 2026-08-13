# NEXT work unit (classify the static VI scalar's semantic use)

HYPOTHESIS-ID: m3-vi-argument-state-origin

Perform one bounded source-only audit. Enumerate every caller of
`getBootConfigField14` (`0x8006B3E0`) and every generated load/reference of
`D_80037574`/`0x7574($v0)`. Trace whether the ROM-initialized `0x00E0` is
used as a display-mode field, a timing/geometry scalar, or only as an
indirect compatibility accessor. Do not add a probe, guard, or game-logic
change; no build or run is needed.

## Competing hypotheses

- H-static-field-display-mode: the scalar is consumed by the VI/display-mode path.
- H-static-field-timing-state: the scalar is consumed as frame timing or geometry state.
- H-static-field-compat-accessor: the accessor is dead or serves an unrelated boot/config path.
- H-static-field-use-unresolved: callers or the data flow remain unavailable in the generated tree.

## Discriminating measurement

For each caller, identify the destination/use of the returned halfword and
whether it reaches `initVideoSubsystem`, `advanceVideoFrame`, or a display
mode/timing structure. A complete call/use chain selects one of the first
three hypotheses; no caller or unresolved indirect dispatch selects the last.

## Exact commands

```sh
rg -n -C 12 "getBootConfigField14|0x8006B3E0|0X7574|D_80037574|80037574" ../N64Recomp/RecompiledFuncs/funcs_*.c src patches syms
rg -n -C 10 "jal.*8006B3E0|call.*getBootConfigField14|jal.*8006B3E0" ../N64Recomp/RecompiledFuncs/funcs_*.c
rg -n "D_80037574|80037574|0x7574|0X7574" ../N64Recomp/RecompiledFuncs src patches docs syms
```
