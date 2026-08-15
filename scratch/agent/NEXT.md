# NEXT work unit (s1225)

HYPOTHESIS-ID: retail-entry-capability

The s1224 audit selected H2: `mainGameLoop` consumes `0x130B30..32`, but the
only writers are idle initialization, save-slot restoration, and reset/default
paths. The save-slot writer is reached from `loadSaveDataIfNotLoaded`, not from
controller polling, so these bytes are not a justified debugger target.

Work unit: perform a bounded generated/companion audit of the boot/input
transition after `runIdleFramesAndLoadSaveData`, centered on
`loadSaveDataIfNotLoaded` and its callers. Identify the first event that can
change retail-entry state after the idle loop, or prove the remaining path is
save/reset-only. Do not build, run, or write an oracle target in this unit.

Competing hypotheses and discriminator:
- H1: a caller or callee in the post-idle load/input chain contains a concrete
  input-controlled retail-entry transition, yielding a justified future
  oracle target.
- H2: the post-idle chain is save/reset-only and retail entry is driven by an
  unmodeled front-end/event path, so no target write is justified.
- H3: the consumer/caller boundary is incomplete or malformed and requires
  symbol or regeneration work before the entry route can be named.

Discriminator: enumerate every call from `loadSaveDataIfNotLoaded` and every
caller that follows the idle loop, then classify its state writes and input
dependencies. A concrete input-controlled transition selects H1; only
save/reset/event-free paths select H2; missing or malformed boundaries select
H3 and stop oracle work.

Exact commands:
```
rg -n -C 8 "loadSaveDataIfNotLoaded|classifySaveStateFromInput|pollControllerInputs|initIdleDemoTimersAndSave" \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c
rg -n "mainGameLoop|runIdleFramesAndLoadSaveData|loadSaveDataIfNotLoaded|classifySaveStateFromInput" \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files
rg -n "loadSaveDataIfNotLoaded|classifySaveStateFromInput|D_80130B10" \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/docs \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files
```

Read bounded windows around every exact hit and record the complete consumer /
caller table in the ledger. If H1 selects a target, the following iteration
must define whole-RDRAM, VI, and debugger-write positive controls before any
oracle run.
