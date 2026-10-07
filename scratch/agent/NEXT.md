# Next work unit: repeat M5 Step 4 with a bounded clean-run harness

HYPOTHESIS-ID: m5-step4-gate-consumer-edge

The s4167 canonical pair reached both target phases and selected
H-upstream-zero-payload. Before treating that as stable, run the same two
arms once through a self-cleaning harness that records and kills the complete
process group. Do not change a gate or consumer.

Exact work: use the already-built Debug binary. Launch the real-image and
`ROGUESQ_AUDIO_UCODE=0` arms from `build/` in parallel, with
`ROGUESQ_STUB_MISSING_FUNCS=1`, `ROGUESQ_LLE_FORCE=1`,
`ROGUESQ_LLE_UNGATED=1`, `ROGUESQ_LLE_SOLO=1`, `ROGUESQ_SPIN_YIELD=1`, the
validated AUTOPILOT schedule, `PROBE_PHASE_WIDTH=1024`,
`PROBE_KEYS_FROM_PHASE=1`, `PROBE_LEAVE_OK=1`, and `ROGUESQ_LOG_ALL=1`.
Capture absolute logs under a new `scratch/agent/soak_results/` directory;
kill the whole process group with SIGKILL after title and hangar are seen.

Competing hypotheses and discriminator:

- H-upstream-zero-payload: both arms again reach title/hangar, the gate stays
  `0x01`, and source/consumer PCM rows match at zero while only the real image
  has DMEM/DMA work.
- H-gate-parity: the port gate/writer transition differs from the retail
  control or the real arm changes a downstream slot/PCM join.
- H-route-invalid: either arm misses the whole-RDRAM-equivalent positive
  control or fails to reach VI 1024 and VI 512.

The discriminating table is phase-keyed and must contain: route phases,
audio dispatch/fields, image exit and DMA count, gate writer/value, service
and slot/status rows, PCM source, and PCM consumer. A missing target phase is
unevaluable. If the clean pair reproduces s4167, keep H-upstream-zero-payload
and choose the next producer-context probe; otherwise fix the harness before
interpreting audio nulls.
