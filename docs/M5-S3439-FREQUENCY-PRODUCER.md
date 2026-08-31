# M5 Session 3439 — frequency producer boundary

The independent retail arm ran first with a whole-RDRAM positive control. The
control reached 10,000 callbacks, both title origins and the hangar origin
were observed, and all four selected predecessor PCs executed: `0x80001B04`
12,652 times, `0x80001CB8` 11,527 times, `0x80006EFC` 1,504 times, and
`0x80006F5C` 5,407 times.

The port was rebuilt once and run on the qualified LLE/spin-yield route. It
reached title 1024 at `0x00790400` and hangar 512 at `0x006AB400`; phase,
caller, wrapper, and image-stage controls fired, with no crash or abort
markers. The new phase-scoped `osSendMesg_recomp` census reached its 512-row
per-origin bound. Of the captured producer rows, 486 used queue
`0x8010FEE0`; 490 published message value zero, and seven published message
value one. The existing caller census retained the expected high-count sites
(`152/52/22/8` for the four selected sites), and the wrapper retained 256
rows.

This does not select a producer-versus-later-boundary hypothesis: the retail
arm observed execution at the selected receive callsites, while the new port
arm observed sends, and no like-for-like retail send publication table was
collected. Queue identity alone is not an exact normalized-tuple join, and the
producer rows use a different register context from the receive rows. The
result is `H-EarlierBoundaryUnevaluable` for this census. It does establish
that the port producer hook is live and that the dominant observed publication
to `0x8010FEE0` is a zero message, but it does not establish whether that
publication is legitimate or identify the missing input.

No waits, slots, dispatch, clear behavior, or PCM writeback changed.

Evidence: `scratch/agent/s3439_m5_frequency_oracle/oracle.log`,
`scratch/agent/s3439_m5_frequency_producer/run.log`, and
`scratch/agent/s3439_m5_frequency_producer/results.txt`.
