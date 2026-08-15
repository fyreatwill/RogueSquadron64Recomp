# NEXT work unit (s1226)

HYPOTHESIS-ID: retail-entry-capability

The s1225 audit selected H2 for the post-idle chain: `loadSaveDataIfNotLoaded`
only reads/copies EEPROM data, `classifySaveStateFromInput` has no generated
caller, and the post-load loop has controller polling/render/account-unlock
work but no input-controlled writer to the retail state bytes.

Work unit: perform a bounded generated/companion audit of the caller and
boot-config path that enters `mainGameLoop` after `runIdleFramesAndLoadSaveData`.
Identify the first concrete retail-entry event or external/front-end handoff;
if the caller path is event-free, prove that the missing transition is outside
the generated game path. Do not build, run, or write an oracle target in this
unit.

Competing hypotheses and discriminator:
- H1: the caller/boot-config chain contains a concrete input-controlled or
  event-controlled retail-entry transition.
- H2: the generated path enters `mainGameLoop` unconditionally after setup and
  the missing retail transition is an unmodeled front-end/event handoff.
- H3: the caller or boot-config boundary is incomplete/malformed and requires
  symbol or regeneration work before the entry route can be named.

Discriminator: enumerate every caller of `mainGameLoop`, its boot-config
producer/consumer, and the exact calls immediately before and after the entry.
A concrete input/event-dependent transition selects H1; an unconditional
generated entry with no such transition selects H2; missing or malformed
boundaries select H3 and require regeneration/source repair before oracle work.

Exact commands:
```
rg -n -C 10 "mainGameLoop|gBootConfig|boot config|0x8003DFA0|8003DFA0" \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c
rg -n "mainGameLoop|gBootConfig|8003DFA0|boot" \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/docs \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files
```

Read bounded windows around every exact hit and record the complete caller /
boot-config table in the ledger. If H1 selects a target, the following
iteration must define whole-RDRAM, VI, and debugger-write positive controls
before any oracle run.
