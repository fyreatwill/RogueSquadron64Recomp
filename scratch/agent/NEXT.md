# Next work unit (s4339): C88C source/branch witness

HYPOTHESIS-ID: m5-step9-retail-port-field-join

The s4338 qualified in-process autopilot run passed the host positive control,
title VI 1024, hangar VI 512, and both filter controls. It emitted 256 C88C
descriptor rows and 256 joined direct rows. The retained retail C904 phase-512
table and port C88C descriptor stream had no ordinal or stable address-offset
payload match, selecting a pre-filter route/stream divergence. The external
field-key arm remains parked as route-invalid.

Competing hypotheses:

- H-descriptor-mapping: port C88C has the same retail source/branch sequence,
  but its descriptor argument or words are mapped differently.
- H-pre-filter-stream: the port C88C source/branch sequence itself diverges
  before descriptor selection.
- H-probe-semantic-mismatch: the existing C88C descriptor rows are not the
  semantic counterpart of retail C904 despite the shared object boundary.

Discriminator: add one phase-gated port witness for the C88C helper's fields
corresponding to retail C904 `s1`, `source_word`, `source_byte`, and
`branch_state`; compare keyed source/branch sequences against the retained
retail table in one run. Matching source/branch sequence with different
descriptor words selects H-descriptor-mapping. Divergent source/branch sequence
selects H-pre-filter-stream. A non-corresponding field shape selects
H-probe-semantic-mismatch and requires a new boundary, not another join field.

Run requirements:

1. Use the existing qualified in-process autopilot route only, with the
   retained seeded save, `M4_Y8000_WIDTH=512`, LLE/solo/spin-yield, and real
   audio.
2. Build once with the new witness and run one phase-gated capture. Require
   host positive control, title VI 1024, hangar VI 512, and nonzero joined
   C88C/direct rows before interpreting the comparison.
3. Do not use the external field-key arm, alter decoder/RSP/AI behavior, or
   add a mitigation.

Exact prior-run artifacts:

- port capture: `scratch/agent/s4338_c904_c88c_join/run.log`
- retail table: `scratch/agent/oracle_s4335_c904_field.log`
- recipe: `scratch/agent/s4338_c904_c88c_join.sh`
