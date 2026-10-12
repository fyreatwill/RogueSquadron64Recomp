# M5 A13 drain boundary — session 4693

The single rebuilt binary was run in two concurrent port arms from `build/`:
the default-off drain tick and `ROGUESQ_DRAIN_INLOOP_TICK=1`. Both arms passed
the positive title (`1024`, `0x00790400`) and hangar (`512`, `0x006AB400`)
controls.

The default-off arm entered the drain with active slots at `0x02`, reached an
all-zero slot snapshot, and returned at 100,000 iterations without firing the
10,000,000-iteration timeout. The tick-on arm kept nine slots at `0x02`
through 10,000,000 iterations, fired `[drain-timeout]` at 10,000,001, and
then returned through the forced-idle path. Both arms had the existing audio
task/PCM controls and status-service activity; no drain behavior change was
made.

The independent Rice oracle passed its whole-RDRAM control (6,671,911
writes), reached title and hangar VI phases, wrote the target status range
`0x154620..0x1658A0` 6,646,657 times and the adjacent control range
`0x153620..0x154620` 15,254 times, and executed the named retail status
writers `0x8009B7CC` and `0x8009B7EC` six times each. The hangar rows included
the same `0x02 -> 0x00` writer pair, although the requested writer-PC rows
were observed at multiple 512-wide origins.

This selects H-A13-retail-status-reap for the covered default port route and
rules out H-A13-port-tick-needed: the explicit in-loop tick is not required
and actively prevents terminal status progress in this capture. The tick-on
timeout is a control failure, not evidence for a new guard. Retail and port
are independent lines for the status-writer family; exact field-to-origin
mapping remains limited to the existing port witness. The timeout guard and
default-off policy remain unchanged.

ORIGIN: no mitigation; this session added only the capture driver and evidence.
