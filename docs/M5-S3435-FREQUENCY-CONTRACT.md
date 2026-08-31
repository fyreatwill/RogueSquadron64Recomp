# M5 Session 3435 — frequency writer input contract

The independent retail oracle ran for 75 seconds with a whole-RDRAM positive
control, physical target `0x165ED0:0x165ED4`, both observed title origins,
`0x800331E0` execution and field watches, and post-value sampling.

The positive control reached 10,000 callbacks. The `0x800331E0` execution
watch reached 141,159 hits. Phase-gated field tuples were not stable: the
`0x00790400` bucket had 3,735 distinct tuples and the `0x00790800` bucket had
4,088 distinct tuples. The target post-value watch retained 701 samples with
64 distinct values; 450 were `0x00000001`. The retained explicit target rows
were in the 512-width bucket and all showed `value=0x00000001`.

This selects `H-Multiple331E0Inputs`. It refutes `H-Stable331E0Input` at the
phase-gated execution scope. It does not establish which input subsets produce
the nonzero frequency result, because the capture did not provide a direct
join between each target post-value and one field tuple. `H-PhaseJoinMissing`
therefore remains a possible instrumentation limitation for that finer join,
not the explanation for the observed multiplicity. No port code or audio
behavior changed.

Raw capture: `scratch/agent/s3435_m5_frequency_contract/oracle.log`.
