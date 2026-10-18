# Next work unit: normalized M4 boundary evidence gate
HYPOTHESIS-ID: m4-shared-boundary-revisit

Implement and run `tools/analyze_m4_normalized.py` against the existing retail
RSM1/RSD1 capture and port M4-key capture. The analyzer must require, in both
arms, positive-control rows plus `(phase_epoch, ucode_overlay_id,
mapped_imem_pc, progress_bucket)`, task-end masks, and at least 20 shared rows
per mapped PC. It must never substitute framebuffer origin, local task serial,
or stage ordinal for a missing normalized field.

Competing hypotheses:

* H1: >=20 shared normalized rows per mapped PC have matching transient-lane
  distributions and zero task-end masks in both arms.
* H2: >=20 shared rows exist, but a repeated lane or writer-PC distribution
  mismatch remains; only then is writer attribution authorized.
* H3: a required field/control is absent in either arm, or fewer than 20 shared
  rows can be formed; the M4 thread remains parked without mitigation.

Discriminator: one analyzer invocation must print positive-control status for
whole-RDRAM/VI/mapped-PC observations, field-presence status for both arms,
shared-row counts per mapped PC, and exactly one verdict H1/H2/H3. The existing
captures are expected to select H3 if the port lacks real task-step and image
identity observations. Self-test must exercise both a passing control and a
missing-field rejection before any capture is interpreted.

Exact commands:

    python3 tools/analyze_m4_normalized.py --self-test
    python3 tools/analyze_m4_normalized.py --retail <RSM1> <RSD1> <oracle.log> --port <port-log>

Expected outcomes: self-test exits 0; the capture run exits 0 only for H1/H2
and exits 2 for H3, with the reason naming the absent field/control. No code
or mitigation follows an H3 result.
