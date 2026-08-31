# M5 s3441 — post-receive frequency consumer edge

The required retail ground-truth arm ran first with a whole-RDRAM positive
control, title origins `0x00790400`/`0x00790800`, and hangar driving. The
control reached 10,000 writes. The selected execution PCs were live: 8,758
hits at `0x80001B04`, 7,728 at `0x80001CB8`, 1,282 at `0x80006EFC`, and 2,680
at `0x80006F5C`; target-phase rows were present.

The regeneration-safe port witness was added immediately after the four
generated `osRecvMesg` callsites. It is phase-scoped to 1024-wide title origins,
requires successful receipt from queue `0x8010FEE0`, and records the callsite,
queue/message-slot join fields, post-receive state pointer, and its first two
state words. The build completed successfully.

The first concurrent pair had a known pre-phase scheduler crash in the image
arm, so it was discarded as a qualification. The corrected `exec`-in-subshell
pair reached the target phase in both arms with no crash or abort markers. Each
arm passed the witness positive control and retained 512 receive rows plus 512
producer rows. The relevant queue consumers were live at `0x80001B04` (358
rows) and `0x80001CB8` (154 rows); the service-call PCs did not consume the
frequency queue and therefore emitted no rows under the queue filter.

All successful port receives consumed message zero, matching the retail
queue/message/flag contract established in s3440. The first downstream state
pointer was populated in both arms, including the same observed `0x801B2950`
state family at the `0x80001CB8` consumer. Silent and image arms differed only
in naturally animating downstream values; both had the same consumer callsite
coverage and positive controls.

This selects `H-RetailConsumerParity` at the observed post-receive boundary:
the queue message reaches a live downstream consumer in both port arms, and no
consumer-edge absence or port-only state loss was observed. It does not prove
that the zero message is semantically correct, nor does it close later output
use. No waits, slots, dispatch, clear behavior, or PCM writeback changed.

Evidence: `scratch/agent/s3441_retail_consumer_groundtruth/oracle.log`,
`scratch/agent/s3441_m5_frequency_consumer_pair/`, and
`tools/apply_s3441_m5_frequency_consumers.py`.
