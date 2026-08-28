# NEXT work unit — M5 producer-mark route-handoff boundary

HYPOTHESIS-ID: m5-route-producer-mark-boundary

Run one new retail-grounded route-handoff probe centered on
`bufferArbiterProducerMark` at `0x8001BCE4` and its caller/consumer. Preserve
the whole-RDRAM positive control and title/hangar VI controls. Do not change a
gate, wait, voice guard, or output destination.

Competing hypotheses and the discriminator:

- H-PortMissingMark: retail executes ProducerMark in the target phase but the
  port has no corresponding producer-mark edge before its 640 stop.
- H-PortWrongCaller: the port reaches the producer region, but a different
  caller/consumer or ordering edge prevents the handoff.
- H-RouteFailure: the port has no target phase, so producer-mark and downstream
  audio nulls are unevaluable.
- H-RetailControlFailure: the retail watch or phase controls are absent, so no
  port conclusion is allowed.

The single discriminator is one phase-keyed table containing the retail
ProducerMark execution PC, predecessor, arguments, VI origin/width, the port
route-state/producer-mark rows and predecessor, and the port title/hangar
phase controls. Whole-RDRAM and retail title/hangar must both be positive.
Retail positive plus port mark absent at 640 selects only a route boundary,
not a causal fix. Port mark present with a different caller/order selects
PortWrongCaller. Missing target phase selects RouteFailure and leaves target
rows unevaluable.

Ground-truth command first:

    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 90 --watch-write 0x0:0x800000 --watch-pc 0x8001BCE4 --vi-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start

Then build once and run a new port-side batched producer-mark capture using
the existing M5 route controls plus the same phase gates. Store the result in
`scratch/agent/s3041_m5_producer_mark_boundary/`.

No behavior change is authorized by this probe. If the port remains before
title, record RouteFailure and pivot the next unit; do not repeat this input
recipe or interpret audio nulls.
