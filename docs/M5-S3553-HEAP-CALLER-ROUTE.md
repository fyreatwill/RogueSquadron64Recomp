# M5 session 3553 — caller table was route-invalid

The regeneration hook added a phase-scoped caller table at both generated
heapFreeListDequeue edges, 0x800104A8 and 0x80010CD8. Each row records the
edge, phase, ordinal, four arguments, node pointer, and relevant saved state.
The table is behavior-neutral and uses the same phase/ordinal reset scheme as
the existing callee entry table.

The first capture command used a nonexistent probe path and produced no game
process. The corrected run passed the autopilot positive control, reached VI
640, and emitted 64 caller rows, all from edge 0x80010CD8 in pre-title phase
3. It emitted 32 heap-entry rows, but never reached VI 1024 or VI 512. The
caller rows therefore cannot be joined to the target-phase entry rows and do
not select H-CallerA, H-CallerB, or H-AlternatePath.

A fresh full regeneration built successfully but also stalled at VI 640.
Restoring the preserved generated tree and rebuilding did not reach the target
gate in this capture either. This is a route-requalification result, not
evidence that edge 2 supplies the target entries.

ORIGIN: diagnostic-only caller instrumentation; no heap, audio, PCM, image,
output, or texture-record value was changed.
