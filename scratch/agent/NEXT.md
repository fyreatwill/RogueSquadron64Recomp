# Next work unit: qualify the next M5 audio contract edge

HYPOTHESIS-ID: m5-step4-gate-consumer-edge

The maintenance iteration compacted CURRENT-TRUTH and ran no experiment.
Next, inspect Step 4 of `docs/M5-AUDIO-PLAN.md` and qualify its named
gate/consumer edge with one rebuilt port and independent retail ground truth.
Batch the real-image and silent arms in the same build/run; do not repeat Step
3 staging or the pre-clear census.

Competing hypotheses and discriminator:

- H-gate-or-consumer-edge: the named Step 4 edge changes a downstream
  slot/PCM join when its writer and value match retail.
- H-upstream-zero-payload: the edge remains unchanged because the source is
  already zero before the consumer boundary.
- H-route-invalid: whole-RDRAM, title VI 1024, or hangar VI 512 controls fail,
  so no gate/consumer conclusion is allowed.

Discriminating measurement: require positive controls plus phase-keyed tuples
through task/SP completion, slot/status transition, PCM source, and consumer.
Select H-gate-or-consumer-edge only if the named edge changes in the declared
real-image arm while silent is the rollback control; select H-upstream-zero-
payload only if both arms prove zero before that edge.

Run from `build/`, capture each arm separately, and kill games with SIGKILL.
