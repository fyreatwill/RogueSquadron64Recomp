# NEXT work unit (s1234)

HYPOTHESIS-ID: retail-reset-entry-equivalence

Run one bounded static source/config audit comparing the retail R4300 reset
entry state with the port's `recomp_entrypoint`. Enumerate the retail core's
`g_start_address`/reset-vector initialization and first boot transition, then
the port's entrypoint, initial register/context setup, and first idle/video
thread creation. Do not build or run.

Competing hypotheses and discriminator:

- H1: retail begins from a reset/vector or initial-state contract that the
  port does not reproduce, explaining the stable VI-320 divergence.
- H2: both paths establish equivalent game entry state, so reset entry is not
  the missing retail transition.
- H3: the paths differ only in a documented non-state configuration such as
  core emulator mode or ROM setup; the difference cannot explain the entry
  state by itself.

Discriminator: a side-by-side entry-state table covering reset PC, reset
register/RDRAM setup, ROM/boot handoff, and first generated call. A concrete
unmatched state-setting operation selects H1; equivalent contracts select H2;
only documented emulator/configuration differences select H3.

Exact commands:

```
rg -n -C 8 'g_start_address|start_address|A4000040|reset|main_run|ROM_OPEN|M64CMD_EXECUTE' /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/src/main /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/src/api
rg -n -C 8 'recomp_entrypoint|entrypoint|run_thread_function|r29|r31|osCreateThread|idle_thread_handle|thread3_video_handle' src ../N64Recomp/RecompiledFuncs/funcs_0.c ../N64Recomp/RecompiledFuncs/funcs.h
rg -n -C 5 'A4000040|80000000|recomp_entrypoint|g_start_address' /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
```

Record the first state-setting operation and first generated/retail call on
each side, then state which hypothesis the complete table selects.
