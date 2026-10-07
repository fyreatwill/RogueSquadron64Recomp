# Next work unit: qualify M5 upstream producer context

HYPOTHESIS-ID: m5-step4-upstream-producer-context

The s4169 clean pair selected H-port-writer-parity: both arms reached the
target phases, recorded the retail-matching port gate writers, and hangar PCM
remained zero. The next discriminator is the producer context feeding the
zero-valued image/task payload; do not change a gate, writer, or consumer.

Exact work: use the already-built binary and run the retail oracle plus the
port real-image arm concurrently with
`scratch/agent/run_s4148_m5_source_callsite.sh` as the harness template. Keep
the whole-RDRAM oracle positive control, title/hangar phase gates, and
`ROGUESQ_LOG_M5_SOURCE_CONTEXT=1`, `ROGUESQ_LOG_M5_SOURCE_PRODUCER=1`,
`ROGUESQ_LOG_M5_PRODUCER_INPUT=1`, `ROGUESQ_LOG_M5_TASK_CONTRACT=1`, and
`ROGUESQ_LOG_PCM_BOUNDARY=1`. Capture retail writer PCs for the source span,
port `0x800078EC` callsite/context/destination/value rows, image task input
hash/nonzero state, task completion, and PCM source/consumer joins in the same
run. Kill the process group with SIGKILL after both target phases.

Competing hypotheses and discriminator:

- H-producer-context-parity: port `0x800078EC` context and source-span writer
  behavior match retail, while the image task input is already zero; the gap is
  before or outside this producer context.
- H-producer-context-mismatch: port context, callsite, destination, or source
  writer/value differs from retail and explains the zero task input; select the
  exact mismatching writer/context for the next audit.
- H-route-invalid: either arm misses the positive control or fails to reach VI
  1024 and VI 512, making writer/PCM nulls unevaluable.

The discriminating table is phase-keyed and must contain: route phases,
positive control, retail source-span writer PCs/values, port producer
callsite/context/destination/value rows, image input hash/nonzero state, task
exit/DMA count, and PCM source/consumer. A missing target phase is unevaluable.
If producer parity holds, keep H-upstream-zero-payload and move earlier in the
producer chain; if it fails, select the specific context mismatch without
changing behavior.
