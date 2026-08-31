# M5 Session 3429 — setup-state entry census

The independent retail oracle ran first with a whole-RDRAM positive control,
Rice video, the validated Start schedule, and execution watches at
`0x80091B84` and `0x80091848`. It reached title 1024 and hangar 512; the
control produced 10,000 writes. Retail observed 9,753 executions at
`0x80091848` and none at `0x80091B84`. The former is an instruction inside
`initN64RspMixer`, and the latter is an instruction inside
`initAudioSubsystem`, not either named function's entry.

Added a regeneration-safe, phase-gated witness at the actual generated entries
of `initAudioSubsystem` (`0x80091B3C`) and `reapplyAudioConfig` (`0x80091C88`).
The Debug build succeeded. Concurrent silent and Factor 5 image arms both
reached title 1024 and hangar 512 with the init positive control and audio
ABI/DMA controls live; image-stage was live only in the image arm, and neither
emitted crash or abort markers.

Each port arm reported one `reapply` entry row at title with
`a0=0x80165ED0, a1=0x12, a2=0, a3=0`; no target-phase `init` entry row was
observed. This run does not measure the proposed `0x5622` mixer-count boundary.
It refutes interpreting the requested labels as the function entries and leaves
the producer question unevaluable at those labels. The next census witnesses
the real `setDisplayMode` callsites at `0x8008EA78` and `0x8008EBC0`.

Evidence: `scratch/agent/s3429_m5_setup_state_producer/oracle.log` and
`scratch/agent/s3429_m5_setup_state_producer/{silent,image}.log`.
