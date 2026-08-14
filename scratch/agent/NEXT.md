# NEXT work unit (s1107)

HYPOTHESIS-ID: submit-producer-boundary

Add regeneration-safe generated-store probes for every `MEM_B`, `MEM_H`, and
`MEM_W` whose resolved physical target can be `0x11A89F` or `0x11A8A0`.
Record phase, store PC, width, address, value, and the next submit-boundary
row; do not change queue behavior. Apply the probe through the normal fixup
path, build, and run the same VI-1024-gated capture with the positive VI/E9
controls and `ROGUESQ_LOG_SUBMIT_BOUNDARY=1`.

Competing hypotheses:

* H-generated-writer: a generated store writes the nonzero `0x8011A8A0` value.
* H-nongenerated-writer: no generated store fires before the nonzero submit
  row, so ownership is outside generated game code or is an alias/write path
  not covered by the store census.
* H-observation-race: the store probe and submit rows do not establish order
  because the shared guest-PC/value observation is cross-thread or the phase
  scope is wrong.

Discriminator: a writer row for `0x11A8A0` preceding a same-phase SP send
selects H-generated-writer; positive controls plus repeated nonzero submit
values and zero generated-writer rows select H-nongenerated-writer; missing
phase/order controls make the capture invalid and require fixing the probe.

Exact baseline command:

```sh
env ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_SLOT_SP_GUARD=1 ROGUESQ_LOG_SUBMIT_BOUNDARY=1 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_LEAVE_OK=1 zsh tools/probe.sh scratch/agent/submit_boundary_writer 60 1.0
```
