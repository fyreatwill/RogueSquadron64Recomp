# NEXT work unit — validate task-start pointer guard on qualified route

HYPOTHESIS-ID: m3-host-entry-pointer-guards

Session 3357 added a full-width KSEG0 guard before every `OSTask`
dereference in the active strong `osSpTaskStartGo_recomp` override. The Debug
target built successfully, but no game route was run in that change unit.

Competing hypotheses:

- `H-TaskPtrAlwaysValid`: valid task/SP completion and title/hangar VI controls
  remain unchanged after the guard.
- `H-TaskPtrWrongRangeModel`: the predicate rejects a legitimate task pointer;
  task dispatch or route controls disappear.
- `H-TaskPtrCorruptionReachable`: the guard fires on an invalid task pointer;
  the game avoids the former host-entry dereference failure.

Discriminator: run the existing validated AUTOPILOT/phase-gated task, host,
title `1024`, and hangar `512` recipe once from `build/`, with the normal
positive controls. Any task/SP/VI continuity selects `H-TaskPtrAlwaysValid`
and refutes the range-model hypothesis; a guard-fire row plus continued
process selects `H-TaskPtrCorruptionReachable`. Do not add another pointer
guard or alter audio behavior.

Exact commands:

```sh
rg -n -C 5 'osSpTaskStartGo_recomp|rs64_guest_range_valid|TO_PTR\(OSTask' src/main/upstream_compat.cpp
cmake --build build --config Debug --target RogueSquadron64Recomp
```
