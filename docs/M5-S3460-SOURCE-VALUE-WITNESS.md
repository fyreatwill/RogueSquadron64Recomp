# M5 s3460 source-value witness

The first prescribed capture crashed during startup at guest PC `0x8000834C`
before title and produced no probe rows. An unchanged retry reached title VI
1024 at origin `0x00790400`, so the retry is the qualified arm.

The new regeneration-safe entry control fired once, followed by 64 bounded
title entry rows. The existing source-writer witness emitted 1,024 rows at the
same title origin: 768 at PC `0x800644B0` and 256 at PC `0x80064524`. The
captured source-store values were zero. The phase line, entry control, and
store rows establish that the title gate, writer function, and relevant stores
all execute.

This refutes `H-WitnessGate`, `H-GeneratedRoute`, `H-TitleNoStore`, and
`H-ControlFailure` at the observed title scope. It does not yet prove whether
zero is the legitimate port value or a port-side contract defect, because the
retail and port writer/value rows were not captured in one controlled join.
The run later changed to width 640 and crashed in `musyxSynthFrame+4268`
(guest PC `0x80001B08`), after the qualified title rows.

Evidence: `scratch/agent/s3460_m5_source_value_witness/run.log` and
`scratch/agent/s3460_m5_source_value_witness_retry/run.log`.
