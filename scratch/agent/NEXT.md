# NEXT work unit (s1106)

HYPOTHESIS-ID: submit-producer-boundary

Perform one phase-gated runtime capture of SP gate bytes `0x8011A89F/0x8011A8A0`,
the DP handler object at `0x8011A408`, and both blocking consumers. Do not
change queue behavior.

Competing hypotheses:

* H-runtime-writer: a runtime writer or producer PC supplies a nonzero gate
  before the blocked consumer.
* H-gate-stale: the bytes remain zero and the producer branch stays suppressed
  while the consumer blocks.
* H-gate-alias: the watched fixed addresses do not correspond to the runtime
  object/field actually read by the producer or DP handler.

Discriminator: phase-gated value writes plus producer/consumer PC records, with
positive VI/E9 controls in the same run. A nonzero write before producer send
selects H-runtime-writer; zero gate values plus producer-side branch misses and
consumer blocking selects H-gate-stale; producer/handler PCs using a different
physical object selects H-gate-alias. A null target result is valid only if
the positive controls fire in that same phase.

Exact commands:

```sh
env ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_SLOT_SP_GUARD=1 ROGUESQ_LOG_DPC=1 zsh tools/run-phase-capture.sh <recipe>
```
