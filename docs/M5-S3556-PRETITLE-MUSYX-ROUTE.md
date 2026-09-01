# M5 s3556 — pre-title MusyX boundary requalified

The required static census found that port guest PC `0x80001B08` is the delay
slot of `osRecvMesg` in `rs_malloc`, not an instruction in `musyxSynthFrame`.
Retail ground truth independently watched the whole-RDRAM write control and
got 10,000 callbacks, but saw zero execution hits in
`0x80001ACC:0x80001B20` over 2,662 VIs. The retail range is therefore not a
direct execution counterpart for the port-only crash label.

The Debug build added a regeneration-safe, phase-gated table around the port
`rs_malloc` entry, message receive, heap-state load, and return. The canonical
real-audio/LLE-solo/spin-yield/autopilot run passed the autopilot control,
emitted 168 phase records, reached the 512 hangar phase, and kept the existing
slot-dispatch table live. The new table emitted:

| edge | rows |
|---|---:|
| entry | 2,759 |
| pre-recv | 10,068 |
| post-recv | 10,068 |
| heap-read | 4,279 |
| return | 10,068 |

No crash marker appeared before deliberate SIGKILL. The run therefore does not
reproduce the s3555 pre-title failure and selects `H-StaleCrashLabel` at this
boundary: the old `musyxSynthFrame+3828`/`0x80001B08` report is not a stable
boundary for the validated route. This does not explain the separate s3554
slot-dispatch crash and does not prove the heap values legitimate beyond this
capture.

Evidence: `scratch/agent/soak_results/s3556_pretitle_musyx/run.log`.

ORIGIN: diagnostic-only route table; no mitigation, guard, or value rewrite
was added.
