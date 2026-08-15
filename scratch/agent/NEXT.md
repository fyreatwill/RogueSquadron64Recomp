# NEXT work unit (s1228)

HYPOTHESIS-ID: external-retail-entry-route

The s1227 audit selected H2: `gBootConfig+0x04` is a static ROM initializer
(`ROM 0x38160 + 4 = 0x8003DFA0`), not a runtime writer. The generated path
registers and invokes `mainBootstrapWorker` normally.

Work unit: perform a bounded source audit of the external/front-end retail
entry route. Trace the oracle's Mupen startup/reset state, controller handoff,
and first state-changing event against the port's `start_game`/entrypoint
setup. Do not build, run, or write a target state.

Competing hypotheses and discriminator:
- H1: the oracle/front-end starts from a different reset or save/input state,
  and its first missing transition is identifiable in source.
- H2: the oracle enters the same static boot path; the later retail transition
  requires an unavailable front-end capability or external state.
- H3: the port and oracle use different entrypoint/bootstrap semantics, so the
  comparison is invalid until that mismatch is named.

Discriminator: identify one concrete state-changing event after the first
320-width phase and the code path that delivers it. A source-visible reset,
save, or input-state difference selects H1; identical static boot with no
callable later-entry capability selects H2; an entrypoint/bootstrap mismatch
selects H3.

Exact commands:
```
rg -n -C 10 "start_game|entrypoint|M64CMD_(RESET|STATE)|savestate|press|PIF|controller" \
  tools/oracle src/main lib/N64ModernRuntime/librecomp/src
rg -n -C 8 "osResetType|gBootConfig|mainBootstrapWorker|mainGameLoop|idle_thread" \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/main_overlay.txt
```
