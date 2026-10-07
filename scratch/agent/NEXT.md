# Next work unit: discriminate the next store/link tuple inside 0x8008F900

HYPOTHESIS-ID: m5-step4-object-entry-body

Session 4184 restored the canonical route and qualified the body witness. The
port reached both target phases and produced 130 body rows. In the shared
hangar phase, the independent retail `--watch-pc` rows and port body rows
matched on `a0/a1/a2`, `s0/s1`, and the first derived store value. The open
boundary is after that first body store pair.

Competing hypotheses:

- H-next-store-parity: the second body store/link tuple is also retail-parity,
  moving the boundary farther inward.
- H-next-store-mismatch: the second store/link tuple diverges, selecting the
  first divergent body input.
- H-target-route-invalid: either positive control or a target phase fails;
  body comparison is invalid and no conclusion is allowed.

Discriminator: extend the existing oracle/port body recipe so the retail arm
captures the second body store/link result at `0x8008F900`, then run one paired
phase-gated measurement with the canonical port settings:
`ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a'`
and `ROGUESQ_AUTOPILOT_STOP_WIDTH=512`. Preserve the whole-RDRAM positive
control, both title origins (`0x00790400`/`0x00790800`), both hangar origins
(`0x006AB400`/`0x006AB800`), and the existing entry/body rows. Matching second
store/link tuples select parity; a mismatch selects the first divergent body
input; missing controls or target phases selects route-invalid. Do not change
audio, gate, writer, payload, or mitigation behavior.

Exact run after the bounded oracle capture is added to the committed recipe:
`zsh scratch/agent/run_s4182_m5_object_body.sh`.
