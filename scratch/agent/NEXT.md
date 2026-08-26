# NEXT work unit (s2453) — identify the port replacement for the retail dispatcher boundary

HYPOTHESIS-ID: m5-port-dispatcher-replacement

## Work unit

Perform one bounded source/runtime audit of the port-side call boundary that
replaces retail `__osDispatchThread/0x8002BEEC` before `0x800078EC`. Start from
the existing generated `rs_memset` execution helper and runtime dispatch path;
enumerate candidate host/runtime entry points and their immediate caller
identity in one table. Do not change behavior or add a new diagnostic field.

## Competing hypotheses and discriminator

- H-PortRuntimeDispatcher: one runtime dispatcher entry replaces the retail
  boundary and can be named from the existing execution path.
- H-PortGeneratedAlternate: the port uses the known generated
  `0x8008F2CC`/`after_6` path, with no dispatcher-equivalent handoff.
- H-PortMultipleBoundaries: more than one port entry reaches the callee, so the
  retail predecessor is not a one-to-one port boundary.

The discriminator is a complete candidate table containing each entry symbol,
its immediate caller/continuation, and whether it can reach the exact
second-range store path. One unique runtime entry selects
H-PortRuntimeDispatcher; only the `0x8008F2CC` generated path selects
H-PortGeneratedAlternate; multiple complete entries select
H-PortMultipleBoundaries. An incomplete table is non-discriminating.

## Exact commands

`rg -n -C 8 "rs64_m5_second_execution|second_execution|800078EC|dispatch|enqueue_external|submit_rsp_task" src lib/N64ModernRuntime ../N64Recomp/RecompiledFuncs --glob '*.{c,cpp,h}'`

`rg -n -C 8 "8008F2CC|rs_memset\\(rdram, ctx\\)|after_6" ../N64Recomp/RecompiledFuncs/funcs_23.c`

`rg -n -C 5 "__osDispatchThread|8002BEEC|800078EC" syms ../N64Recomp/fixup_game_funcs.py src lib/N64ModernRuntime`
