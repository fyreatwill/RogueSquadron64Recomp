# Next work unit: qualify the port M5 gate/consumer edge

HYPOTHESIS-ID: m5-step4-gate-consumer-edge

Retail ground truth is complete in s4166: the whole-RDRAM oracle control
fired, target phases were reached, and `0x800A0F50` was written by five PCs;
`0x8008EC88` is the observed nonzero writer. Candidate watches at
`0x80094648`, `0x80090AAC`, and `0x80090BA4` had no retail writes. Qualify
port parity and downstream behavior; do not change a gate yet.

Exact work: build once with `cmake --build build --config Debug --target
RogueSquadron64Recomp`; run the real-image and `ROGUESQ_AUDIO_UCODE=0` arms
from `build/` in parallel using `tools/probe.sh`, phase-gated with
`PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1`, and enable
the existing M5 writer/route/task/PCM categories plus `ROGUESQ_LOG_ALL=1`.
Capture the two logs under distinct absolute `scratch/agent/soak_results/`
directories and SIGKILL each process group after both title and hangar phases.

Competing hypotheses and discriminator:

- H-gate-parity: port records the retail writer/value transition, and one
  downstream slot/PCM join changes in the real-image arm versus silent.
- H-upstream-zero-payload: both arms reach the target phases and match through
  the gate, but the source remains zero before the consumer edge.
- H-route-invalid: either port arm lacks the whole-RDRAM-equivalent control,
  title `1024 @ 0x00790400`, or hangar `512 @ 0x006AB400`.

Discriminating measurement: one phase-keyed comparison table for both arms
containing gate writer/value, task/SP completion, service/status/slot, PCM
source, and consumer joins. Select H-gate-parity only if the port writer/value
matches the retail PCs and the real arm changes a downstream join; select
H-upstream-zero-payload only if both arms prove zero before the edge.

The oracle evidence is in `scratch/agent/retail_step4_values.log`; do not
repeat the retail run unless the port measurement exposes a route mismatch.
