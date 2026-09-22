# M5 s3717 — exact PCM consumer queue join

The consumer callback now records its phase-local ordinal and SDL queued-byte
snapshot through `n < 256`, so the image-stage `pcm_consumers_seen` field can
be joined to the exact consumer row.

The first fixed-budget paired retry was invalid because the silent arm stalled
at title. A later retry again stalled the silent arm, while the real arm
reached hangar origin `0x006AB400` and passed the existing task/SP completion
controls. The valid real-arm sample contained 191 image-stage rows: stage 2
had 96 rows with 31 queue matches and 65 mismatches; stage 3 had 95 rows with
31 matches and 64 mismatches. Thus 129/191 image rows saw queue depth different
from the consumer row named by `pcm_consumers_seen`.

This selects `H-AudioDrainNotConsumed` for the measured port-side boundary and
rejects `H-AudioDrainParity` in that sample. It also rejects the earlier simple
low/drained-threshold explanation: the image-stage queue values continue to
vary while the exact consumer ordinal does not expose the same snapshot.
Because the silent arm did not reach hangar and the retail oracle could not run
without its debugger-enabled Mupen64Plus core, this is single-source port
evidence; it is not a retail callback-parity claim.

ORIGIN: diagnostic-only callback snapshots. The legitimate producer and
consumer are the existing `osAiSetNextBuffer` SDL queue path and PCM callback;
no audio behavior or mitigation was changed.
