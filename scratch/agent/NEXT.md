# NEXT work unit (s1233)

HYPOTHESIS-ID: retail-entry-boundary

Run one bounded static audit of the remaining external retail-entry boundary:
enumerate the ROM/decomp and installed-oracle startup paths that can alter
execution state after `ROM_OPEN` and before the first stable VI-320 loop.
Include EEPROM load, reset/state commands, SDL input attachment, and any
front-end callback or savestate handoff. Do not build or run; this is one
source/config census.

Competing hypotheses and discriminator:

- H1: the front-end/core has an unenumerated state-changing route that can
  explain the missing retail entry.
- H2: startup only opens ROM/save media, attaches input, and executes; the
  missing event is outside the available oracle/front-end contract.
- H3: the retail-entry boundary is actually an EEPROM/core-format issue, shown
  by a mismatch between selected media, load semantics, or ROM configuration.

Discriminator: a complete startup-event table. A previously unknown
state-changing command/callback selects H1; a complete ROM-open-to-execute
contract with no such route selects H2; a media/config/load disagreement
selects H3.

Exact commands:

```
rg -n -C 5 'ROM_OPEN|M64CMD_EXECUTE|M64CMD_RESET|M64CMD_STATE_LOAD|M64CMD_STATE_SAVE|SDL|EEPROM|eeprom|savestate' tools/oracle ../rogue_squadron64 ../mupen64plus* 2>/dev/null
rg -n -C 4 'CoreStartup|ROM_OPEN|STATE_LOAD|EXECUTE|EEPROM|savestate|reset' /usr/local/include /opt/homebrew/include /usr/local/src /opt/homebrew/src 2>/dev/null
rg -n -C 4 'mainBootstrapWorker|mainGameLoop|gBootConfig|8003DFA0' ../N64Recomp/RecompiledFuncs ../rogue_squadron64/symbol_files
```

Record each startup event as ROM-open, media load, input, state command, reset,
or indirect handoff, and state whether it can occur before the first stable
VI-320 loop.
