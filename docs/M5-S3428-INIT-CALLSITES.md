# M5 Session 3428 — direct initN64RspMixer callsites

The independent retail oracle ran first with a whole-RDRAM positive control,
Rice video, the validated Start schedule, and watches at
`0x8009189C`, `0x80091C58`, and `0x80091D14`. It reached title 1024 and
hangar 512; the control produced 10,000 writes. Retail observed two calls from
`0x80091D14` and none from `0x80091C58`.

Added a regeneration-safe phase-gated witness immediately before both generated
callsites. The fresh Debug build succeeded. Concurrent silent and Factor 5
image arms both reached title 1024 and hangar 512 with the init positive
control, audio ABI/DMA controls, and (image arm only) image-stage control live;
neither emitted crash or abort markers.

Both arms reported `caller=0x80091D14` in title and hangar, with the same
arguments as the prior init witness. No `0x80091C58` row occurred in either
arm. This selects `H-PortCallerD1D14`, matching retail, and refutes
`H-PortCallerD1C58` and `H-PortCallerUnresolved` at the observed route. The
caller site is closed; the earlier producer of port `a1=0x5622` remains open.
No runtime behavior changed. Evidence is in
`scratch/agent/s3428_m5_caller_groundtruth/oracle.log` and
`scratch/agent/s3428_m5_caller_pair/{silent,image}.log`.
