# Next work unit: M5 alternate family-object ownership discriminator

HYPOTHESIS-ID: m5-alternate-family-object-ownership

The s3829 target-phase DMA census closed the missing-descriptor question at its
qualified scope: no `rs64_m5_audio_source_dma` callback occurred during title
1024 or hangar 512, while target-VI, route, lifetime-DMA, and exact-DMA-hook
controls were positive. The next unit must explain the 1,280 S/L/I stores and
257 family-entry rows that remain outside the clear-associated object without
repeating the completed aliasing join.

Competing hypotheses and discriminator:

- H1: the alternate objects are legitimate guest route state or a separate
  output family; their bases and entry rows remain stable and correlate with
  family site/route ordinal even though no target-phase RSP source DMA consumes
  them.
- H2: the family is disconnected/stale output; alternate-object entries do not
  correlate with accepted route handoff or any target-phase consumer.
- H3: the family is a CPU-side stage whose consumer is outside the current RSP
  callback; the stores correlate with target-phase task/service or PCM rows but
  not with the absent RSP source-DMA path.

The discriminator is one target-valid image run with a bounded ownership table
covering every family entry/store row in both target phases, joined in the same
row to family site, object base/span, route ordinal/row, route handoff,
audio-task ordinal, PCM-source/consumer ordinal, and target phase. H1 is stable
object/site/route correlation; H2 is positive family activity with no route,
task, or PCM join; H3 is positive task/PCM correlation with no RSP-source-DMA
join. Keep the existing whole-RDRAM/phase, family, route-prep/order/transition/
handoff, task, PCM, and DMA-hook positive controls live.

Before running, inspect the existing family-entry/store and task/PCM markers
and add the complete joined table in one batch; do not add isolated counters.
Build and run from the repository root:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    env ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_DRAIN_INLOOP_TICK=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_M5_FAMILY_EDGE=1 ROGUESQ_LOG_M5_FAMILY_STORE=1 ROGUESQ_LOG_M5_ROUTE_PREPARE=1 ROGUESQ_LOG_M5_ROUTE_ORDER=1 ROGUESQ_LOG_M5_ROUTE_TRANSITION=1 ROGUESQ_LOG_M5_ROUTE_HANDOFF=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_PCM_WRITER=1 ROGUESQ_LOG_M5_RSP_SOURCE=1 ROGUESQ_LOG_M5_EXACT_ROUTE=1 ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a' ROGUESQ_AUTOPILOT_STOP_WIDTH=512 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 ./RogueSquadron64Recomp

Use SIGKILL cleanup, retain `scratch/agent/s3830_m5_family_ownership/`, and
reject the run if either target phase or any positive control is absent.
