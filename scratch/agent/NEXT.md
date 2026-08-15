# NEXT work unit (s1224)

HYPOTHESIS-ID: retail-entry-capability

The s1223 census selected H2: `D_80130B10+0x20..22` at physical
`0x130B30..32` are reset/idle transition bytes, not a later retail-entry
control surface. `runIdleFramesAndLoadSaveData` is the only direct non-reset
writer (`B30=1`, `B31=0`); `B32` has no direct generated writer. The main loop
consumes these bytes after the idle routine.

Work unit: perform a bounded generated/companion audit of every `mainGameLoop`
consumer of `B30..32` and its upstream boot/input transition callers. Identify
the first state-changing event after the idle initializer, or prove the chain
has no reachable input-controlled producer. Do not build, run, or write an
oracle target in this unit.

Competing hypotheses and discriminator:
- H1: a later input-controlled producer or transition feeds the consumed
  state, yielding a justified future oracle target.
- H2: the idle initializer is the terminal producer and retail entry is driven
  by another event/call path, so no state-byte write is justified.
- H3: the consumer/caller boundary is incomplete or malformed and requires
  symbol or regeneration work before the entry route can be named.

Discriminator: enumerate every `mainGameLoop` load of offsets 0x20, 0x21, and
0x22, then trace each branch's called function and all upstream callers back to
the idle initializer. A later input-controlled producer selects H1; only the
idle/reset producer with downstream consumers selects H2; missing or malformed
boundaries select H3 and stop oracle work.

Exact commands:
```
rg -n -C 8 "MEM_BU\([^\n]*0X2[012]" \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_8.c
rg -n "mainGameLoop|runIdleFramesAndLoadSaveData|pollControllerInputs|loadOverlay" \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files
rg -n "func_8003E07C|func_8003E0DC|D_80130B10" \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/docs \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files
```

Read bounded windows around every exact hit and record the complete consumer /
caller table in the ledger. If H1 selects a target, the following iteration
must define whole-RDRAM, VI, and debugger-write positive controls before any
oracle run.
