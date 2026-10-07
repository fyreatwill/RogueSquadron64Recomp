# Next work unit: trace the first producer/caller of the divergent object fields

HYPOTHESIS-ID: m5-step4-object-field-producer

Use the qualified s4174 route as the base. The port-side witness at
`0x80090268`, `0x80090278`, and `0x8008FF04/0C/14` fired in title/hangar, but
its `s0+0x60`, `s0+0x22`, and `s1+0x22` values did not reconcile with the
independent retail oracle. Do exactly one phase-gated producer-context
instrument build/run. Retain the oracle whole-RDRAM positive control,
`--pc-field-dump`, `PROBE_PHASE_WIDTH=1024`, `PROBE_KEYS_FROM_PHASE=1`,
real-audio/LLE/ungated/solo route, and all existing source/object/task/image/
PCM joins. Add one port witness at the first generated producer/caller that
supplies the object base or the divergent pointed fields; persist it through
`../N64Recomp/fixup_game_funcs.py`.

Before building, compare the new witness against these hypotheses:

- H-earlier-producer-mismatch: the port producer/caller emits a legitimate
  object or field value different from retail; this moves the boundary earlier.
- H-object-layout-alias: the producer values reconcile after normalizing the
  port allocation/layout relation; the s4174 mismatch was an address alias.
- H-route-invalid: either independent positive control or title/hangar phase
  is absent; object nulls are unevaluable.

The discriminator is one same-run table joining producer PC/caller, object
base, the selected field values, and the existing five-PC rows in both retail
and port. No audio, gate, writer, payload, or mitigation behavior change is
authorized.
