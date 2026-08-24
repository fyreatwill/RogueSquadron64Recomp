# NEXT work unit (s2290) — same-build stub route requalification after retail slot-route match

HYPOTHESIS-ID: m5-step2-route-requalification

## Work unit

Build the unchanged current tree once, then run one stub-first/default-second
comparison using the established eleven-Start port route plus the full
phase-keyed route/audio table. The s2289 oracle proved that retail executes
the equivalent slot-dispatch route at initial `640 @ 0x00696100`; s2288's
port arm was launched directly without a host key injector and crashed in
`slotDispatcherIter+3508` / guest PC `0x80007904`. The new driver must inject
the same Start scancodes into the port window rather than assuming that
`PROBE_KEYS_FROM_PHASE` drives a directly launched executable. Do not change
runtime audio selection or add a guard, skip, writeback, C88 override, or
route workaround.

## Competing hypotheses and discriminating measurement

- H-PortStubRouteRestored: with the established input route explicitly
  driven, the stub control reaches title `1024 @ 0x00790400` and hangar
  `512 @ 0x006AB400`; the driver then launches the default image and its
  complete task/DMA/service/slot/voice/PCM row can be compared.
- H-PortCallbackStateGap: the driven stub still reaches the initial 640 route
  but dies at `0x80007904` or another missing-function/callback boundary before
  title/hangar; the retail-equivalent route does not by itself restore the
  port's callback/list state, so the default arm remains unlaunched.
- H-RouteControlInvalid: the independent retail whole-RDRAM/title/hangar
  controls or the port's input/VI route control is absent; all audio nulls are
  unevaluable and the run must not launch or interpret the default arm.
- H-DefaultSafe: only if H-PortStubRouteRestored is selected and the default
  arm reaches the same title/hangar phases with the complete table
  `dispatch → task ABI/source → DMEM/DMA → image exit → SP completion →
  service → status/slot → voice/reap → PCM source/consumer`.

The discriminator is one same-build, phase-gated driver matrix: independent
retail positive control first; port stub with explicit Start scancodes; then
default image only after the stub hangar gate. For each arm retain initial-640
route ordinal, guest terminal/missing-function marker, title/hangar phase,
and every M5 task/output row. A `Broke` return or audio dispatch alone is only
a branch control. A missing stub gate vetoes all default-arm interpretation.

## Exact commands

1. Build once:

   `cmake --build build --config Debug --target RogueSquadron64Recomp`

2. Create the self-contained driver
   `scratch/agent/run_s2290_m5_stub_route_requal.sh`. It must launch the
   oracle and port arms itself, inject Start scancode 40 on the port route,
   gate on VI transitions, retain all captures, SIGKILL every remaining
   process in cleanup, and exit nonzero when a required control is absent.

3. Check and run exactly that driver:

   `zsh -n scratch/agent/run_s2290_m5_stub_route_requal.sh`

   `zsh scratch/agent/run_s2290_m5_stub_route_requal.sh`

If the stub title/hangar gate is absent, classify H-PortCallbackStateGap or
H-RouteControlInvalid from the measured terminal/control row and do not launch
the default arm. No default promotion follows from this work unit alone.
