# M5 Session 3438 — frequency caller boundary

The retail ground-truth arm watched `0x800331D0` with a whole-RDRAM positive
control, both title origins, and the field dump. The control reached 10,000
writes; the entry produced 95,359 execution hits and 7,806 unique normalized
field tuples in the bounded phase rows.

The fresh-build port image arm used the validated LLE/spin-yield route and
reached title 1024 and hangar 512. Phase, audio-task, RSP-source, PCM, and
spin-yield controls fired; there were no crash or abort markers. The caller
census at all generated `osRecvMesg` callsites emitted 256 rows and 107 unique
tuples. The existing wrapper census emitted 256 rows and the same 107 tuples;
their exact intersection was 107. The caller set had zero intersection with
the retail set. The main caller sites were `0x80001B04` (152 rows),
`0x80001CB8` (52), `0x80006EFC` (22), and `0x80006F5C` (8).

This selects `H-EarlierPortInputGap`: the retail-observed normalized family is
absent before the port wrapper at the observed scope. It refutes
`H-PortWrapperContractGap`, since every observed port caller tuple survived
unchanged into the wrapper, and it refutes `H-EarlierBoundaryUnevaluable`,
since the caller control and target phases were live. This does not identify
the earlier producer or establish that any port tuple is illegitimate.

The first port attempt was invalid because it omitted `ROGUESQ_SPIN_YIELD=1`
and stayed in the 640 cinematic phase; its zero marker count was discarded.

Evidence: `scratch/agent/s3438_retail_frequency_ground_truth/oracle.log` and
`scratch/agent/s3438_m5_frequency_input_retry/run.log`.
