# M5 s3442 — frequency first output use

The independent retail oracle passed its whole-RDRAM positive control with
93,638,451 writes, reached 3,572 VI frames, and executed both selected load
sites in the driven route: `0x80001C0C` 7,875 times and `0x80001CC8` 7,630
times. The sites were live in the 1024 title and 512 hangar phases.

The fresh-build port pair passed its consumer and output positive controls.
Both silent and image arms reached title and produced 343 joined output rows;
the image retry also reached the same result without crash or abort. The
first tuples matched between arms, including `0x80001CC8` output `0x2`, with
the existing `(queue,msg,callsite,state)` join fields present.

This proves the first post-consumer output use is present in both port arms
and that the retail output sites are live, but the oracle execution watch
does not expose a value-level queue/state join. Therefore output-value parity
with retail is not established, and no port output divergence is claimed.
The result is `H-OutputValueJoinUnevaluable` at this boundary. No waits,
slots, dispatch, clear behavior, or PCM writeback changed.

Evidence: `scratch/agent/s3442_retail_output_sites.log`,
`scratch/agent/s3442_m5_frequency_output_pair/`, and
`scratch/agent/s3442_m5_frequency_output_pair/image_retry.log`.
