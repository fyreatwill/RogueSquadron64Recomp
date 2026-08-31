# NEXT work unit — separate retail indirect execution from host dispatch

HYPOTHESIS-ID: m5-callback-indirect-pointer-source

Session 3345 completed the static provenance audit. `initN64RspMixer` builds
the stored callback value `0x80007910` as an immediate immediately before
`0x80091900`; there is no source address/value load to capture. The later
`0x800919D4` reload and `0x800919EC` `jalr` are confirmed in the same body.
The source-writer question is therefore closed; the remaining question is
whether retail's zero execution-watch count is a host-dispatch path or an
execution-watch attribution gap.

Session 3344 selected `H-PointerWriter`: retail passed the whole-RDRAM,
title-1024, and hangar-512 controls, and wrote the corrected physical slot
`0x001499D4` six times, all from guest PC `0x80091900`. The execution watch
had zero hits. The port aggregate arm independently recorded the corresponding
`0x80091900 -> 0x80007910` store edge. `H-StalePointer` is closed for this
route; the next unit must attribute the writer's source value and test whether
the watched slot is later consumed indirectly.

Competing hypotheses:

- `H-HostDispatch`: the slot write is incidental and host/runtime dispatch
  supplies the effective callback without a guest indirect execution.
- `H-ExecutionWatch`: the zero execution count is a watch/attribution gap;
  the slot is consumed through an uninstrumented or differently-addressed
  indirect path.
- `H-GuestJalr`: retail executes the guest indirect edge, but the existing
  execution watch misses it or attributes it outside the requested range.

The next discriminating measurement is an independent retail run with a
positive control plus an execution attribution watch covering both the exact
`0x800919EC` guest PC and the loaded target `0x80007910`, while retaining the
corrected physical slot watch. A target hit at the guest `jalr` supports
`H-GuestJalr`; a slot write with no guest edge plus a host callback marker
supports `H-HostDispatch`; a slot write with neither requires reopening the
watch attribution. Do not build the port: its immediate source is already
proven and the existing port transfer marker is at the exact edge.

Exact static commands:

    rg -n -C 35 '0x80091900|0x800919D4|0x800919EC' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c
    rg -n -C 12 'initN64RspMixer|registerSiCallback|MEM_W\(0X[0-9A-F]+, ctx->r' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c | head -240

If the audit names a concrete source site, add one regeneration-surviving
probe through the applicable `tools/apply_s*.py`, build once with
`cmake --build build --config Debug --target RogueSquadron64Recomp`, and run
the existing phase-gated title/hangar recipe with
`env ROGUESQ_LOG_M5_CALLBACK_WRITER=1`.
