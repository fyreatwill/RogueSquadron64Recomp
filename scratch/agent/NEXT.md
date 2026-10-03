# Next work unit: join alternate-family events to route handoff/service events

HYPOTHESIS-ID: m5-alternate-family-object-ownership

Session 3832 established that 882/882 target-valid family rows followed their
matched image-stage event, while PCM source/consumer match IDs stayed zero.
The remaining question is whether that post-stage family activity is an
intended route/service step or disconnected output.

Competing hypotheses and discriminator:

- H1: the alternate family is intended CPU-side route work. Family events join
  the same task generation, route row, and route-handoff/service event, with a
  stable order across repeated rows.
- H2: the family is stale/disconnected output. Family events do not join the
  route-handoff/service event once the shared event sequence is used, despite
  the earlier image-stage/task-generation join.
- H3: the family is a distinct post-stage service branch. Family events join
  the same route/service epoch but consistently occur after the handoff, with
  no PCM source/consumer join.

The discriminator is one target-valid image run with the existing monotonic
join event stamp added to route-handoff/service records. Emit one bounded row
containing event kind, event sequence, task generation, route ordinal/row,
phase, and the family/stage/hand-off relationships. H1/H2/H3 must be selected
from the complete joined table, not wall-clock order or separate counters.
Keep positive controls: target VI 1024 and 512, family entry/store, image
stage, route preparation/order/transition/handoff, source-range, task, PCM,
and exact-DMA controls. The retail oracle remains unavailable with the
Homebrew core because `DebugSetCallbacks` requires a DEBUGGER=1 build; do not
treat that setup failure as a null.

Before building, add the handoff/service stamp to the existing callbacks in
`src/main/main.cpp`; do not edit generated functions or the runtime submodule.
Then run:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_AUTOPILOT='3:start,7:start,11:start,15:a,30:start,45:start,60:a' PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_M5_FAMILY_EDGE=1 ROGUESQ_LOG_M5_FAMILY_STORE=1 ROGUESQ_LOG_M5_TASK_LIFETIME=1 ROGUESQ_LOG_M5_STAGE_CALLS=1 ROGUESQ_LOG_M5_STAGE_BYTES=1 ROGUESQ_LOG_M5_RSP_SOURCE=1 ROGUESQ_LOG_M5_PCM_WRITER=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 ROGUESQ_LOG_M5_EXACT_ROUTE=1 ROGUESQ_LOG_M5_SOURCE_TRANSITION=1 ROGUESQ_LOG_M5_ROUTE_ORDER=1 ROGUESQ_LOG_M5_ROUTE_TRANSITION=1 ROGUESQ_LOG_M5_SOURCE_RANGE=1 ROGUESQ_LOG_M5_ROUTE_PREPARE=1 ROGUESQ_LOG_M5_ROUTE_HANDOFF=1 ROGUESQ_LOG_M5_DYNAMIC_CALLBACK=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 zsh tools/probe.sh scratch/agent/s3833_m5_family_handoff_order 180 0.5

Reject the run unless both target phases and every listed positive control are
present. Use SIGKILL cleanup and compute event-order counts from the bounded
joined rows.
