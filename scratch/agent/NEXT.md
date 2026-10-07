# Next work unit: discriminate the loop-control tuple after 0x8008F910

HYPOTHESIS-ID: m5-step4-object-entry-body

Session 4185 qualified the canonical route with an oracle physical watch and
exact `--store-field-dump`/post-store controls for `0x8008F90C` and
`0x8008F910`. Retail and port matched the shared hangar store/link addresses,
and both exact retail PCs had nonzero, mismatch-free post-store scalar samples.
The oracle callback does not expose a stable written-value field, so the
conclusion is limited to address/link and scalar-write parity. The open
boundary is after the second body store/link tuple.

Competing hypotheses:

- H-loop-control-parity: the post-store increment/compare tuple at
  `0x8008F914`/`0x8008F918` is retail-parity, moving the boundary to the loop
  branch target.
- H-loop-control-mismatch: the increment/compare tuple diverges, selecting the
  first divergent post-store input.
- H-target-route-invalid: either positive control or a target phase fails;
  body comparison is invalid and no conclusion is allowed.

Discriminator: add a regeneration-safe port witness at the first instruction
after the matched stores (`0x8008F914`) and an oracle `--watch-pc`/field capture
for `0x8008F914` and `0x8008F918`, then run one paired phase-gated measurement
with the canonical port settings:
`ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a'`
and `ROGUESQ_AUTOPILOT_STOP_WIDTH=512`. Preserve the whole-RDRAM positive
control, both title origins (`0x00790400`/`0x00790800`), both hangar origins
(`0x006AB400`/`0x006AB800`), and the existing entry/body rows. Matching loop-
control tuples select parity; a mismatch selects the first divergent
post-store input; missing controls or target phases selects route-invalid. Do
not change audio, gate, writer, payload, or mitigation behavior.

Exact recipe to extend:
`zsh scratch/agent/run_s4182_m5_object_body.sh`
