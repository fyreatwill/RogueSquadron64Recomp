# NEXT work unit (s1237)

HYPOTHESIS-ID: retail-external-entry-boundary

Run one bounded source census of the remaining external/front-end retail-entry
boundary. Compare every command or lifecycle event between ROM_OPEN and
EXECUTE in `tools/oracle/rs64_oracle.c`, the installed console frontend/core,
and the port's `recomp_entrypoint`; classify each as a possible state-changing
handoff or ordinary setup. Do not build or run.

Competing hypotheses and discriminator:

- H1: an unaccounted front-end/core event changes retail game state before or
  during EXECUTE; the port lacks an equivalent handoff.
- H2: ROM_OPEN-to-EXECUTE has no hidden state-changing event; the missing
  transition is outside the available launcher contract.
- H3: the apparent difference is only emulator/runtime bookkeeping, with no
  game-state handoff at all.

Discriminator: one event table listing source location, lifecycle point,
state-changing side effect, and port equivalent. A concrete unmatched
state-changing event selects H1; a complete matched table selects H2; only
host bookkeeping with no game-state side effect selects H3.

Exact commands:

```
rg -n -C 4 'ROM_OPEN|EXECUTE|STATE_LOAD|STATE_SAVE|RESET|CoreDoCommand|attach|startup|EEPROM|savestate|press' tools/oracle /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-ui-console
rg -n -C 4 'recomp_entrypoint|start_game|load_stored_rom|M64CMD|ROM_OPEN|STATE_LOAD|reset|EEPROM' src lib/N64ModernRuntime/librecomp/src
```

Classify every lifecycle event before choosing the next boundary.
