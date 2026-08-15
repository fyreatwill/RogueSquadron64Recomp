# NEXT work unit (s1223)

HYPOTHESIS-ID: retail-entry-capability

The s1222 census corrected the address identity: `mainGameLoop` reads
`D_80130B10+0x20..22` at physical `0x130B30..32`. `gGameSettings+0x20..22`
at `0x130B60..62` are volume bytes, so the s1219–s1221 oracle writes were not
state-entry tests.

Work unit: perform a bounded generated/companion census of every writer and
caller affecting `D_80130B10+0x20..22`, including reset/demo paths, and identify
one justified target for a future debugger-enabled oracle run. Do not build,
run, or write another oracle target in this unit.

Competing hypotheses and discriminator:
- H1: `B30..32` have a reachable producer beyond the idle reset path; the
  census identifies its writer, call chain, and a future target.
- H2: `B30..32` are reset/transient mission-state bytes and no producer offers
  a retail-entry route; the state-machine gate is downstream of a different
  input or boot transition.
- H3: the generated or companion boundary is incomplete around the mission
  state object; missing intervals or unresolved aliases require regeneration
  or symbol-boundary work before any oracle write.

Discriminator: enumerate exact generated loads/stores of physical `0x130B30`,
`0x130B31`, and `0x130B32`, map all containing functions and callers, then
reconcile with `D_80130B10_type` and `mainGameLoop`. A reachable non-reset
writer supports H1; only reset/clear/consume edges supports H2; missing or
malformed intervals supports H3 and stops oracle work.

Exact commands:
```
rg -n "0X[Bb]10|0X[Bb]30|0X[Bb]31|0X[Bb]32|D_80130B10|gMissionState" \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/docs \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files
rg -n "mainGameLoop|runIdleFramesAndLoadSaveData|resetGameSettingsAndMissionStats" \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c
```

Read bounded windows around every exact hit and record the complete writer /
caller table in the ledger. If H1 selects a target, the next iteration must
define whole-RDRAM, VI, and debugger-write positive controls before running it.
