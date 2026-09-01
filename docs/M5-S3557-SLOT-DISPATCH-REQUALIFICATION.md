# M5 s3557 — slot-dispatch failure did not reproduce

The canonical real-audio/LLE-solo/spin-yield/autopilot capture used the
existing regeneration-safe slot-dispatch table and ran from `build/` for 90
seconds before deliberate SIGKILL. Autopilot fired at VI widths 640, 1024, and
512; the phase log reached title origin `0x00790400` and hangar origin
`0x006AB400`.

The table emitted 2,771 entry rows, 2,048 pre-call rows, and 2,048 post-call
rows, all in phase 3. Every sampled pre-call slot was a valid KSEG0 pointer
(`valid=1`); the slot-SP guard emitted zero rows. No crash marker,
`last-guest-pc`, SIGBUS, or guest PC `0x80007904` failure appeared before the
run was killed. The run continued with hangar presentation after the slot
table budget was exhausted.

This selects `H-SlotCrashAbsent` for the current discriminator: the s3554
failure is route-specific and was absent on the route-valid s3557 capture.
`H-SlotInput`, `H-SlotLifecycle`, and `H-SlotOverlay` are unevaluable here,
because the failing consumer did not execute. The earlier s3554 crash remains
an independent route observation; this run does not identify its writer or
explain it.

Evidence is single-source for this iteration: phase controls and the joined
slot table are in
`scratch/agent/soak_results/s3557_slot_dispatch_requal/run.log`. The prior
s3554 crash is only a separate route comparison.

ORIGIN: diagnostic-only table and SP guard; no mitigation, guard behavior, or
game value was changed.
