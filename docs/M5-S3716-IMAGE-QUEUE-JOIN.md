# M5 s3716 — image-stage queue join

The first two paired launches were invalid: one real arm crashed before
hangar, and the next launcher left the real output at startup while the silent
process continued. The launcher was fixed to wait after process cleanup and
use a fresh output directory. The fixed same-build pair reached title VI 1024
and hangar VI 512 in both arms; both emitted the RSP source positive control.

The new `[m5-image-queue]` row sampled SDL queued bytes at image stages and
carried the phase-local PCM consumer count already seen. In the real arm the
hangar origin produced 190 rows: 95 stage-2 and 95 stage-3. Queue depth ranged
from 0 to 4,581 bytes. The first hangar image-stage row saw 3,045 bytes and
four PCM consumers already seen; later rows included 4,581, 3,301, 2,021,
767, and zero bytes. The silent arm produced no image-stage rows because its
audio RSP arm is the intentional stub, but it reached hangar and emitted its
RSP control.

This rejects a simple `H-AudioStageQueueGate` explanation in which image-stage
execution requires one consistently low/drained queue threshold. It does not
establish retail callback parity and does not yet separate
`H-AudioDrainNotConsumed` from downstream host-state parity: the queue and
consumer observations are single-source port evidence. The next measurement
must attach the exact consumer-row queue snapshot to the image-stage
`pcm_consumers_seen` join key.

ORIGIN: diagnostic-only SDL queue observations. The legitimate producer is the
existing `osAiSetNextBuffer` to SDL queue path; no mitigation or behavior
change was added.
