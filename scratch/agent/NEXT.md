# NEXT work unit (s2397) — identify route-identity preparation ordering

HYPOTHESIS-ID: m5-image-stage-route-identity-order

## State going in

s2396 passed dispatch and title-origin controls and found 140 image-stage call
attempts, but every captured attempt preceded a valid route identity. The
title transition occurred later at phase 8, so the call rows cannot yet be
classified as title-stage calls. `rs64_audio_route_prepare` is the only
known producer of the identity used by the stage route filter.

## Work unit

Add one bounded, phase-scoped witness at `rs64_audio_route_prepare` and one
matching witness at `rs64_audio_image_stage`, sharing a sequence number and
phase/width/origin. Record whether preparation ran before each stage call and
whether it accepted a target route. Keep all behavior unchanged. Build once,
then run one suppressed image-arm instance from `build/` for 60 seconds with
the same route controls and `ROGUESQ_LOG_M5_STAGE_CALLS=1` plus the new
preparation witness. Use the s2392 oracle exact-window result as the existing
ground-truth prerequisite; do not change task data, audio, gate, fallback,
dispatch, VI, output behavior, or mitigation.

## Competing hypotheses and discriminator

- H-RoutePrepareMissingOnStagePath: stage calls have no preceding prepare
  witness; the producer path bypasses route preparation.
- H-RoutePrepareNonTargetOrdering: prepare runs immediately before calls but
  rejects the current width/origin; preparation and call keys match while the
  accepted-target bit is zero.
- H-RouteIdentityClearedBetweenPrepareAndCall: prepare accepts a target route,
  then the stage entry sees `route_valid=0`; the shared sequence/order proves
  a clear or cross-thread identity loss.

The discriminating table is one row per stage 0–3 and call sequence: prepare
count, prepare accepted-target count, call count, call route-valid count, and
the phase/width/origin values. No prepare before a call selects the bypass;
prepare-rejects selects non-target ordering; accepted prepare followed by an
invalid call selects identity clearing.

## Controls and commands

The run must show `[audtask-dispatch]` activity and title origin
`0x00790400` at width 1024. Use the built macOS executable from `build/` with
the existing s2396 route controls, then SIGKILL after 60 seconds. The s2392
oracle exact-window witness is the ground-truth prerequisite.
