# NEXT work unit — widen retail VI publication boundary to the consumer handoff

HYPOTHESIS-ID: m5-retail-video-publication-boundary

## Single work unit

Use the retail oracle to watch the next consumer-side handoff outside the
closed selector/record family. Start from the VI manager/context publication
path after the queued mode is consumed; include a whole-RDRAM positive
control, title/hangar phase controls, and one complete candidate PC/address
set in the same run. Do not repeat `0x800C2984`, `0x8001A098:0x8001BB6C`, or
the selector/record watches from s3121. Do not modify the port.

## Competing hypotheses

- H-ConsumerHandoff: the missing publication is attributed to a consumer-side
  call/store after the queued mode reaches the VI manager.
- H-OutsideConsumer: the descriptor/register writer is outside the next
  consumer candidate set, so the probe must widen again.
- H-DeferredVI: title is reached without a directly attributable write in the
  producer or consumer candidate sets, indicating deferred/frame-boundary
  publication.

## Discriminating measurement

The PC-attributed write/call sequence across the 640-to-1024 transition splits
the hypotheses. A matching consumer write/call selects H-ConsumerHandoff; a
live consumer candidate with no matching publication selects H-OutsideConsumer;
no publication with passed controls selects H-DeferredVI.

## Exact commands

Run the existing retail-oracle recipe from `tools/oracle/README.md`, retaining
the whole-RDRAM positive control and title/hangar phase controls. Use a new
consumer-side candidate set derived from the VI manager/context path and
record the result in `scratch/agent/s3122_*`.
