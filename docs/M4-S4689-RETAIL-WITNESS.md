# M4 retail witness boundary (s4689)

The prescribed same-phase capture rebuilt the Debug target once and ran the
canonical port route beside the independent Rice retail oracle for 120 seconds.

Port controls were positive: stage 1 produced 64 rows, and phase 5 at the
hangar route produced 517 rows at each of stages 10, 11, and 12 plus 497 stage
13 rows. The port reached repeated 512-wide VI origin `0x006AB400`. The later
VI-640 crash-family abort occurred after the target rows had been collected.

Retail controls were also positive: the whole-RDRAM watch recorded 197,474,334
writes, retail reached repeated 512-wide `0x006AB400`, and the narrow watches
recorded 80 writes at `0x006AB400..10` and 1,682 at `0x00656400..10`. The
`osViSwapBuffer` execution witness recorded 1,556 hits, including the target
512-wide phase.

The retail Rice/HLE path does not expose the RSP accumulator, VMADH/VGE
registers, or RSP DMEM to `rs64_oracle`; consequently it emitted no equivalent
stage-10/11/12/13 internal rows. This is a qualified instrument-boundary
result, not a claim that retail failed to reach the render boundary. It selects
H-M4-unreachable for the internal retail witness and leaves the retail-versus-
port accumulator-value comparison unevaluable. No runtime change or mitigation
is authorized.

Evidence: `scratch/agent/s4689_m4_retail_witness/{port.log,oracle.log}`.

ORIGIN: no mitigation; the only change was a phase-gated diagnostic capture
script, and the absent retail internal rows are a limitation of the independent
HLE oracle boundary.
