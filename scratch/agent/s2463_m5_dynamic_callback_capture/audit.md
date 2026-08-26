# s2463 M5 dynamic callback capture

## Ground truth

The retail oracle ran for 60 seconds with Rice video, the RSP-HLE plugin, and
the eleven-Start schedule. Its whole-RDRAM positive control reached the
10,000-hit cap; the run reached the 512-wide hangar origin `0x006AB400` and
recorded 314 executions each of `spawnNpcOfType` and its `0x800400BC` store,
3,220 `slotDispatcherIter` executions, and 26,016 executions of the
`0x8003E974` indirect-call site. The retail watch validates the memory-write
instrument and target phase for this work unit.

## Port capture

The build used `tools/apply_s2463_m5_dynamic_callback.py` and the host helper
in `src/main/main.cpp`. The qualified route and capture env ran for 60 seconds
from `build/`. The port indirect resolver positive control fired once, proving
that the resolver capture was enabled. The port reached phase 4 (`640`, origin
`0x0066A500`) but never reached either target bucket (`1024/0x00790400` or
`512/0x006AB400`). It aborted on `get_function(0)` from
`convertMat3x4ToN64Mtx`, with last guest PC `0x80001F88`.

| source | target-phase rows |
|---|---:|
| `m5-dynamic-callback` | 0 |
| `slot-dispatch kind=pre` | 0 |
| `m5-dispatch-boundary` target | 0 |
| `m5-dispatch-boundary-control` positive control | 1 |

## Result

This is a qualified non-result for `H-ZeroWriter`, `H-ValidWriter`, and
`H-UnresolvedWriter`: the joined tuple is absent because the port dies before
the target phase. It does not establish callback polarity or authorize a
guard, dispatch change, audio change, output remap, or task-data change. The
next work unit must isolate the earliest pre-target null-dispatch boundary
while retaining the resolver positive control.
