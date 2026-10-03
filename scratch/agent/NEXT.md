# Next work unit: stamp authoritative route identity at audio-return

HYPOTHESIS-ID: m5-alternate-family-object-ownership

Session 3833's target-valid handoff capture was instrument-positive but
discriminator-invalid: all target handoff rows had task_generation=0 and did
not share route keys with active family rows. Do not repeat that callback.

Competing hypotheses and discriminator:

- H1: the alternate family is intended route/service work. A stamp emitted at
  `rs64_audio_route_set`/audio-return joins the same task generation, route
  ordinal/row, and event order as family rows.
- H2: the family is stale/disconnected output. The authoritative route stamp
  remains absent or does not join family rows with the same generation and
  route key.
- H3: the family is a distinct post-stage branch. The authoritative route
  stamp joins the same generation and route key, but every family event is
  after the route/audio-return stamp and PCM source/consumer matches remain
  zero.

The discriminator is one target-valid image run whose complete joined table
contains family entry/store events, image-stage events, and an explicit
route-context event emitted where `rs64_audio_route_set` receives ordinal,
row, and the current audio generation. Count exact joins and event ordering;
do not use wall-clock order or route identity without generation.

Before building, add the route-context stamp in `src/main/main.cpp` around the
existing `rs64_audio_route_set` call in `rs64_log_audio_return`; do not edit
generated functions or the runtime submodule. Keep the existing event IDs and
all positive controls from s3833.

Build and run from the repository root:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_AUTOPILOT='3:start,7:start,11:start,15:a,30:start,45:start,60:a' PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_M5_FAMILY_EDGE=1 ROGUESQ_LOG_M5_FAMILY_STORE=1 ROGUESQ_LOG_M5_TASK_LIFETIME=1 ROGUESQ_LOG_M5_STAGE_CALLS=1 ROGUESQ_LOG_M5_STAGE_BYTES=1 ROGUESQ_LOG_M5_RSP_SOURCE=1 ROGUESQ_LOG_M5_PCM_WRITER=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 ROGUESQ_LOG_M5_EXACT_ROUTE=1 ROGUESQ_LOG_M5_SOURCE_TRANSITION=1 ROGUESQ_LOG_M5_ROUTE_ORDER=1 ROGUESQ_LOG_M5_ROUTE_TRANSITION=1 ROGUESQ_LOG_M5_SOURCE_RANGE=1 ROGUESQ_LOG_M5_ROUTE_PREPARE=1 ROGUESQ_LOG_M5_ROUTE_HANDOFF=1 ROGUESQ_LOG_M5_DYNAMIC_CALLBACK=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 zsh tools/probe.sh scratch/agent/s3834_m5_family_route_context 180 0.5

Reject the run unless both target phases and every listed positive control are
present. Use SIGKILL cleanup and classify H1/H2/H3 only from the complete
generation/route/event joined table.
