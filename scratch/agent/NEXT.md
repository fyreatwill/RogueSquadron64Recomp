# Next work unit: direct task-generation join for alternate family objects

HYPOTHESIS-ID: m5-alternate-family-object-ownership

Session 3830 selected H3 only at a bounded scope: target-valid family rows
coincided with active route/task context and queued audio, while target-phase
RSP joins had zero source/consumer matches. The queue snapshot is backlog, not
an ownership proof. Add the missing direct task-generation/route join before
interpreting the alternate objects further.

Competing hypotheses and discriminator:

- H1: alternate objects are the intended CPU-side route state. Family rows
  share the same task generation and route ordinal/row as accepted target-phase
  audio-task handoffs, with stable family/site-to-object mapping.
- H2: alternate objects are disconnected/stale output. Family rows have no
  matching task generation or route handoff despite positive task controls.
- H3: family stores belong to a CPU-side stage whose task generation matches,
  but they occur before/after the RSP task and never match an RSP source or
  consumer DMA join.

The discriminator is one target-valid image run with every family entry/store
row carrying task generation, route sequence/ordinal/row, task ordinal and
PCM source/consumer match IDs. H1 is stable same-generation route ownership;
H2 is no generation/route join; H3 is same-generation CPU/task correlation
with source/consumer DMA matches still absent.

Before building, add the complete row join in one batch. Keep the existing
whole-RDRAM/phase, family, route-prep/order/transition/handoff, task, PCM, and
DMA-hook positive controls live. Build and run from the repository root:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    env ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_DRAIN_INLOOP_TICK=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_M5_FAMILY_EDGE=1 ROGUESQ_LOG_M5_FAMILY_STORE=1 ROGUESQ_LOG_M5_ROUTE_PREPARE=1 ROGUESQ_LOG_M5_ROUTE_ORDER=1 ROGUESQ_LOG_M5_ROUTE_TRANSITION=1 ROGUESQ_LOG_M5_ROUTE_HANDOFF=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_PCM_WRITER=1 ROGUESQ_LOG_M5_RSP_SOURCE=1 ROGUESQ_LOG_M5_EXACT_ROUTE=1 ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a' ROGUESQ_AUTOPILOT_STOP_WIDTH=512 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 ./RogueSquadron64Recomp

Run from build/, retain `scratch/agent/s3831_m5_family_task_join/`, use
SIGKILL cleanup, and reject the run if either target phase or any positive
control is absent.
