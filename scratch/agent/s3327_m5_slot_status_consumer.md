# Session 3327 — M5 slot/status consumer boundary

The ground-truth capture watched whole RDRAM, slot `0x141AD0:0x141AF0`, status
`0x154620:0x1546A0`, and execution PCs `0x80094648`, `0x8009B600`,
`0x8009B85C`, and `0x8009BDE8`.

Retail results: whole-RDRAM produced 58,457 writes; the slot range produced
108 writes; the status range produced 48,349 writes; and the route reached
`512 @ 0x006AB400`. Execution counts were 288, 12,703, 12,703, and 3,758
respectively. This is valid positive-control evidence that retail has
target-phase slot/status activity and executes the named consumer PCs.

The Debug target rebuilt successfully. The first port arm used `ROGUESQ_LOG_ALL`
and reached title `1024 @ 0x00790400`, but excessive logging prevented hangar
qualification. The lighter rerun used the same build and reached the same title
phase, with positive controls of 18,904 task joins, 89 PCM source rows, 89 PCM
consumer rows, and 912 audio-route rows, but still did not reach hangar within
the 120-second SIGKILL watchdog. No crash or abort marker was emitted. The
port-side like-for-like comparison is therefore incomplete; no port
slot/status writer row is claimed.

This selects `H-RetailSlotConsumer` for the independent retail branch. It does
not select `H-PortMatchesRetail`, and authorizes no behavior change or
mitigation. The missing port edge remains open between the image/PCM path and
the slot/status relation. The initial port attempt failed before launch because
this Darwin host has no `timeout` utility (`rc=127`); the explicit PID watchdog
reruns are the valid captures.
