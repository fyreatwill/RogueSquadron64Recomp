# s2482 — post-receive image-task consumer provenance

Date: 2026-08-26

## Static path

The adjacent generated tree places the target receive in
`spTaskSchedulerThread` (`../N64Recomp/RecompiledFuncs/funcs_4.c`). At
`0x80019CD0` it calls `osRecvMesg` with queue `0x8011A420`, receives the fixed
message value `0x80128C70` into its stack frame, and reads the message's first
byte as the event type. The message-type branches at `0x80019CE0` through
`0x80019D00` either continue waiting or enter scheduler handling; none reads
the image-task DMA destinations or an image-route ordinal from the received
message.

The scheduler then consumes its own pending-task state. The relevant paths
load the pending task pointer from `0x801372D8` (the generated address for the
`-0x72C8($at)` state), call `osSpTaskLoad` at `0x80019D58`, `0x80019DDC`,
`0x80019E34`, or `0x80019EB0`, and call `osSpTaskStartGo` immediately after
those loads. This is a generic scheduler/task handoff, not a direct image-DMA
consumer or PCM/output callback.

## Dynamic join

The s2481 target-route capture independently recorded external enqueue,
external delivery, and guest receive for the same queue/message. Its image
join rows still report `source_matches=0`, `consumer_matches=0`, and
`classification=stage-only`; the target image DMA destinations and the later
PCM/slot/voice fields do not join in the capture. The event-wiring rows prove
the receive boundary, while the image-stage/join rows prove the missing
identity handoff beyond it.

## Verdict

`H-LaterConsumer` selected at the first post-receive boundary: the receive
returns into a generic scheduler path whose task pointer is held separately
from the fixed SP message, and no image-task key is retained at this edge.
This does not prove which later slot, voice, PCM, or output consumer is
legitimate. No output remap, task-data change, guard, or runtime behavior
change is authorized.

Evidence is two-source: generated control flow and the independent s2481
runtime/join capture.
