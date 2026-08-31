# NEXT work unit — trace the retail pointer writer's provenance

HYPOTHESIS-ID: m5-callback-indirect-pointer-source

Session 3344 selected `H-PointerWriter`: retail passed the whole-RDRAM,
title-1024, and hangar-512 controls, and wrote the corrected physical slot
`0x001499D4` six times, all from guest PC `0x80091900`. The execution watch
had zero hits. The port aggregate arm independently recorded the corresponding
`0x80091900 -> 0x80007910` store edge. `H-StalePointer` is closed for this
route; the next unit must attribute the writer's source value and test whether
the watched slot is later consumed indirectly.

Competing hypotheses:

- `H-WriterSource`: `0x80091900` stores a legitimate value derived from a
  guest-side source or table in the retail route.
- `H-HostDispatch`: the slot write is incidental and host/runtime dispatch
  supplies the effective callback without a guest indirect execution.
- `H-ExecutionWatch`: the zero execution count is a watch/attribution gap;
  the slot is consumed through an uninstrumented or differently-addressed
  indirect path.

The discriminating measurement is one bounded static provenance audit followed
by one port run only if it identifies a concrete source access: enumerate the
instructions immediately before `0x80091900` and the load at `0x800919D4`, then
capture that source address/value together with the existing callback-writer
rows and `0x800919EC` transfer rows. A guest source load feeding the store and a
matching indirect execution supports `H-WriterSource`; a valid slot write with
no guest execution and a host callback marker supports `H-HostDispatch`; a
different indirect target or source address supports `H-ExecutionWatch`.
Missing host/task/title/hangar controls invalidates the port null. No behavior
change is authorized.

Exact static commands:

    rg -n -C 35 '0x80091900|0x800919D4|0x800919EC' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c
    rg -n -C 12 'initN64RspMixer|registerSiCallback|MEM_W\(0X[0-9A-F]+, ctx->r' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c | head -240

If the audit names a concrete source site, add one regeneration-surviving
probe through the applicable `tools/apply_s*.py`, build once with
`cmake --build build --config Debug --target RogueSquadron64Recomp`, and run
the existing phase-gated title/hangar recipe with
`env ROGUESQ_LOG_M5_CALLBACK_WRITER=1`.
