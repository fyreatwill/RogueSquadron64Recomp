# Next work unit: qualify the next M5 audio contract edge

HYPOTHESIS-ID: m5-step4-gate-consumer-edge

Session 4164 closed the declared-size staging qualification: `0x800` reaches
both target phases with the full measured task/SP/route contract, while the
legacy `0xF80` arm adds DMEM writes without a downstream change. Do not repeat
Step 3 or the pre-clear writer census.

Competing hypotheses and discriminator:

- H-gate-or-consumer-edge: the named Step 4 gate/consumer boundary changes a
  downstream slot/PCM join when its writer and value match retail.
- H-upstream-zero-payload: the named edge remains unchanged because the
  source payload is already zero before it can affect the consumer.
- H-route-invalid: the paired retail/port phase controls do not qualify, so
  no gate or consumer conclusion is allowed.

Discriminating measurement: before changing anything, use the existing
qualified retail writer/value evidence and one rebuilt port with the selected
Step 4 consumer/gate probe. Require whole-RDRAM control, title VI 1024,
hangar VI 512, matching writer/value tuples, and the same phase-keyed chain
through task/SP completion, slot/status transition, PCM source, and consumer.
If the named edge changes a downstream join in the declared arm while the
silent arm remains the rollback control, select H-gate-or-consumer-edge. If
the source is zero before the edge in both arms, select H-upstream-zero-
payload. Missing phase controls select H-route-invalid.

Exact commands: inspect `docs/M5-AUDIO-PLAN.md` Step 4 and the current truth
entry for the named writer/consumer; batch both real-image and silent arms in
one build; run from `build/` with phase-gated controls; kill games with
SIGKILL; capture each arm separately.
