# Next work unit: order alternate family activity against image-stage events

HYPOTHESIS-ID: m5-alternate-family-object-ownership

Session 3831 selected H3 at the completed generation-join scope: target-valid
family rows joined a same-route image-stage task generation, but all sampled
PCM source/consumer match IDs were zero and the independent image summaries
were stage-only. Route identity does not establish causality.

Competing hypotheses and discriminator:

- H1: alternate family writes are the intended CPU-side preparation for the
  image stage. A shared event sequence places the family callback before the
  matching image-stage record for the same route ordinal/row, consistently by
  family/site.
- H2: alternate objects are disconnected or stale output. Family callbacks
  have no same-route event join once the shared sequence is used, or their
  ordering is unrelated across repeated rows.
- H3: the family is a CPU-side stage coupled to the same task epoch but not
  the RSP PCM path. Family events join and consistently precede/follow the
  image stage, while source/consumer PCM match IDs remain zero.

The discriminator is one target-valid image run with a single monotonic host
event sequence stamped at every target-phase family entry/store and every
image-stage registration. Emit the family event, matching stage event, task
generation, route ordinal/row, and PCM source/consumer match IDs in one bounded
table. Positive controls must remain live: whole-RDRAM/phase, family,
route-prep/order/transition/handoff, task, PCM, and DMA-hook controls. Do not
infer order from wall time or from separate counters.

Before building, implement the shared event stamp in the existing RSP join
and family callbacks, export the submodule patch, then run from the repository
root:

    ./submodule-patches/export.sh
    cmake --build build --config Debug --target RogueSquadron64Recomp

Run from `build/`, retain `scratch/agent/s3832_m5_family_event_order/`, use
SIGKILL cleanup, and reject the run if either target phase or any positive
control is absent. Use the validated environment from s3831 and
`PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1`.
