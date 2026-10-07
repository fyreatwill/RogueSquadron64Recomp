# Next work unit: qualify M5 port gate-writer parity

HYPOTHESIS-ID: m5-step4-gate-writer-parity

The s4168 clean pair reproduced H-upstream-zero-payload: both arms reached the
target phases and hangar PCM remained zero. The next discriminator is the
port-side writer/value contract for `0x800A0F50`; do not change a gate or
consumer.

Exact work: use the already-built Debug binary and run both real-image and
`ROGUESQ_AUDIO_UCODE=0` arms concurrently from `build/` using
`scratch/agent/run_s4168_m5_step4_clean_pair.sh` as the harness template.
Enable `ROGUESQ_LOG_M5_GATE_CONTRACT=1`, `ROGUESQ_LOG_M5_WRITER_ENTRY=1`,
`ROGUESQ_LOG_M5_B40_WRITER=1`, `ROGUESQ_LOG_M5_GATE_CONTRACT=1`,
`ROGUESQ_LOG_M5_TASK_CONTRACT=1`, `ROGUESQ_LOG_PCM_BOUNDARY=1`, the same
LLE/route controls, and `PROBE_PHASE_WIDTH=1024`, `PROBE_KEYS_FROM_PHASE=1`.
Capture title/hangar writer PCs, post-store gate values, task completion,
slot/status transitions, and PCM source/consumer joins in one run; use the
whole-RDRAM-equivalent positive control and SIGKILL both arms after the target
phases.

Competing hypotheses and discriminator:

- H-port-writer-parity: port writer PCs/values match the retail writer set,
  gate reaches the observed nonzero state, and downstream rows remain zero.
- H-port-writer-mismatch: a port writer/value differs from retail or its gate
  transition changes task/slot/PCM joins, selecting the exact writer context
  for the next audit.
- H-route-invalid: either arm misses the positive control or fails to reach VI
  1024 and VI 512, making writer/PCM nulls unevaluable.

The discriminating table is phase-keyed and must contain: route phases,
positive control, audio dispatch/fields, image exit and DMA count, every
`0x800A0F50` writer PC/value, service and slot/status rows, PCM source, and
PCM consumer. A missing target phase is unevaluable. If writer parity holds,
keep H-upstream-zero-payload and move to the producer-context boundary; if it
fails, select the specific writer/value mismatch without changing behavior.
