# Next work unit: discriminate the first post-loop load/use

HYPOTHESIS-ID: m5-step4-object-entry-body

Session 4188 selected H-successor-parity at `0x8008F924`: the canonical paired
route qualified its positive control and both title/hangar phases, and retail
and port matched the terminal successor tuple. The first post-loop load is at
`0x8008F928`, reading guest address `0x801499C8`; the next derived operation
uses that loaded value at `0x8008F938` and stores zero at `0x8008F93C`.

Competing hypotheses:

- H-load-parity: port and retail agree on the loaded state and derived address,
  moving the boundary to the post-loop store/caller.
- H-load-mismatch: the loaded value or derived address differs, selecting the
  first divergent loaded/use value.
- H-target-route-invalid: any positive control or target phase fails; no load
  comparison is valid.

Discriminator: add a regeneration-safe witness at `0x8008F928`, `0x8008F938`,
and `0x8008F93C`, plus oracle PC/field capture for the same load/use/store
sequence. Run one paired phase-gated measurement with:

`zsh scratch/agent/run_s4189_m5_object_load.sh`

Preserve the whole-RDRAM positive control, both title origins
(`0x00790400`/`0x00790800`), both hangar origins
(`0x006AB400`/`0x006AB800`), all existing entry/body/loop/branch/successor
rows, and the canonical autopilot with
`ROGUESQ_AUTOPILOT_STOP_WIDTH=512`. Matching load/use tuples select parity;
a mismatch selects the first divergent value; missing controls or target
phases selects route-invalid. Do not change audio, gate, writer, payload, or
mitigation behavior.
