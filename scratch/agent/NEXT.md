# Next work unit (s4400): compare port selector/task payloads on the qualified route

HYPOTHESIS-ID: m5-selector-decode-boundary

The s4399 route is qualified as `0x00790400 -> 0x006AB400`; do not seek or
recount the absent `0x00790800` bucket.

Competing hypotheses:

- H-port-payload-equivalence: selector/decode and task/image payloads match in
  the first-title and hangar buckets; the missing origin is only a route label.
- H-port-payload-divergence: the direct transition still produces
  phase-specific selector/task payload families.
- H-port-payload-instrument-gap: either actual phase, control, or join is
  absent, so no payload conclusion is valid.

Discriminating measurement: one phase-gated run must retain paired selector,
task, image-DMA, and payload-field rows for both actual origins, then report
exact selected-word/payload matches and phase-family hashes. Equal relationships
select equivalence; phase-specific families or zero matches select divergence;
missing control, phase, or joins selects instrument gap.

Exact commands: create `scratch/agent/run_s4400_m5_port_payload_route.sh` with
`apply_patch`, based on
`scratch/agent/run_s4399_m5_port_vi_origin_sequence.sh`; retain all controls
and add only bounded phase-keyed selector/task/payload comparison output. Run
`zsh scratch/agent/run_s4400_m5_port_payload_route.sh` from the repository root
for 85 seconds, SIGKILL the game, and inspect its summary plus bounded counts.

RESUME NOTE (s4400 retry): the first attempt died with no artifacts; start from the work unit above unchanged.
