# Session 3260 — scheduler identity capture

The Debug target built successfully. The documented `build/Debug` directory
does not exist in this Unix checkout, so the same command was run from the
actual `build/` output directory. It ran for the full 60-second watchdog
window and was then SIGKILLed.

The positive controls fired: `submit-boundary`, `vi-recv-path`, and
`recv-scheduler-identity` rows were present. Accepted scheduler rows included
valid guest message pointers and type bytes `0x02`, `0x01`, and `0x81`, with
`89F/28D44` fields captured. This proves the repaired post-return identity
instrument is live and evaluates accepted messages in the same run.

The port reached phase 2 width 320 and then phase 4 width 640 at origin
`0x0066A500`; it never reached the target VI-640 wall or a target-phase row.
There were no crash, abort, Bus-error, access-violation, or last-guest-PC
markers. Therefore the target-phase discriminator is unevaluable: the
observed type-2 rows cannot select `H-SpMsgMutated`, and the absence of a
target-phase type-2 row cannot select `H-Type2AbsentAtRecv`. No scheduler or
audio behavior was changed.

Capture: `scratch/agent/s3260_scheduler_identity.log`.
