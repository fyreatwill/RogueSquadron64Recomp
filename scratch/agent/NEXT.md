# NEXT work unit (s1229)

HYPOTHESIS-ID: external-retail-entry-route

The s1228 audit selected H2 for the in-tree route: the oracle does `ROM_OPEN`
then `M64CMD_EXECUTE`, while the port enters directly at `recomp_entrypoint`;
neither source contains a later retail-entry command. The generated path
registers and invokes `mainBootstrapWorker` normally.

Work unit: perform a bounded source/config audit of the installed Mupen64Plus
front-end/core startup contract beyond `tools/oracle/rs64_oracle.c`. Identify
whether the external launcher supplies a reset type, EEPROM/save image, or
alternate entry command before `M64CMD_EXECUTE`; do not build, run, or write a
target state.

Competing hypotheses and discriminator:
- H1: the installed launcher/core injects reset, EEPROM, save, or entry state
  before execution; that concrete input explains the missing transition.
- H2: the installed launcher supplies no such state; the later retail
  transition is unavailable to the current oracle route.
- H3: launcher and port use different bootstrap/entrypoint semantics, making
  the comparison invalid until that mismatch is named.

Discriminator: find one concrete pre-`EXECUTE` state-changing call or config
load and its target. A reset/save/EEPROM/entry command selects H1; absence of
one in the installed launcher/core selects H2; a different ROM entrypoint or
bootstrap callback selects H3.

Exact commands:
```
rg -n -C 8 "CoreStartup|CoreDoCommand|M64CMD_(ROM_OPEN|EXECUTE|RESET|STATE)|EEPROM|save|entrypoint|reset" \
  /opt/homebrew /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/tools/oracle 2>/dev/null
rg -n -C 8 "ROM_OPEN|M64CMD_EXECUTE|recomp_entrypoint|gBootConfig|mainBootstrapWorker" \
  tools/oracle src/main lib/N64ModernRuntime/librecomp/src \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c
```
