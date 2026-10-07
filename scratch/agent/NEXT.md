# Next work unit: discriminate the post-loop store return/caller

HYPOTHESIS-ID: m5-step4-object-entry-body

Session 4189 selected H-load-use-parity: the corrected canonical paired route
qualified its positive control and both title/hangar phases, and retail and
port matched the load/use/store tuple at `0x8008F928`, `0x8008F938`, and
`0x8008F93C`. The next boundary is the return after the store and the caller
continuation at `0x8008F8A8`.

Competing hypotheses:

- H-return-parity: port and retail agree at the post-store return state and
  caller continuation, moving the boundary to the first caller consumer.
- H-return-mismatch: the stored state, restored return registers, or caller
  continuation differs, selecting the first divergent return state.
- H-target-route-invalid: any positive control or target phase fails; no return
  or caller comparison is valid.

Discriminator: add a regeneration-safe witness at the post-store return delay
slot `0x8008F958` and caller continuation `0x8008F8A8`, plus oracle execution
watches for both PCs. Run one paired phase-gated measurement with:

`zsh scratch/agent/run_s4190_m5_object_return.sh`

Preserve the whole-RDRAM positive control, both title origins
(`0x00790400`/`0x00790800`), both hangar origins
(`0x006AB400`/`0x006AB800`), all existing entry/body/loop/branch/successor/
load rows, and the canonical autopilot with
`ROGUESQ_AUTOPILOT_STOP_WIDTH=512`. Matching return/caller tuples select
parity; a mismatch selects the first divergent return state; missing controls
or target phases selects route-invalid. Do not change audio, gate, writer,
payload, or mitigation behavior.
