# Next work unit: requalify the port route for the 0x8008F900 body witness

HYPOTHESIS-ID: m5-step4-object-entry-body

Session 4182 added the regeneration-safe pre-instruction body witness, but the
paired run was route-invalid on both port arms. Reuse the witness and first
establish a clean port target-phase route, then compare it against the already
qualified retail oracle rows.

Competing hypotheses:

- H-body-input-mismatch: the first qualified body tuple differs between retail
  and port after the matched predecessor context.
- H-body-input-parity: qualified body tuples match, moving the boundary inward.
- H-route-invalid: the port does not reach a target phase; no body conclusion
  is allowed.

Discriminator: one run with the existing build, whole-RDRAM positive control,
both title origins (`0x00790400`/`0x00790800`), both hangar origins
(`0x006AB400`/`0x006AB800`), and joined `0x8008F8FC`/`0x8008F900` body rows.
A qualified tuple mismatch selects the first divergent input; parity moves the
boundary inward; missing port target phases is route-invalid. Do not change
audio, gate, writer, payload, or mitigation logic.

Exact command: `zsh scratch/agent/run_s4182_m5_object_body.sh` after confirming
no stale game/oracle children. The script is self-watching and SIGKILLs both
arms; it uses the already-built body witness and the independent retail oracle.
