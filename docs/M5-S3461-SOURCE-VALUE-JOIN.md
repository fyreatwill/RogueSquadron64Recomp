# M5 s3461 source-writer join attempt

Built the Debug target and ran the prescribed LLE/spin-yield port capture
gated on title VI width 1024. The port reached origin `0x00790400`, and the
same-run writer control fired in the earlier width-640 phase. The title writer
table emitted 1,024 ordered rows: 768 at `0x800644B0` and 256 at
`0x80064524`; every captured port value was `0x00000000`.

The run left width 1024 after 28.7 seconds and later crashed in the existing
`musyxSynthFrame+4268` path at guest PC `0x80001B08`. That crash is after the
qualified title rows and is not evidence about the source-store contract.

The planned discriminator could not be evaluated. The retained independent
retail post-store artifact reports phase/PC totals and value histograms
(`0x800644B0`: 807 zero; `0x80064524`: 269 nonzero), but contains no ordered
phase/PC/value rows or ordinals. Therefore none of parity, legitimate port
zero, wrong value, or writer-route hypotheses is selected. The port result is
qualified; the cross-runtime join is not.

Evidence: `scratch/agent/s3461_m5_source_value_join/run.log` and
`scratch/agent/s3458_m5_source_value/oracle_retry.log`.

ORIGIN: the zero values are generated port source stores at the named PCs;
their legitimacy remains unevaluable because the independent retail sequence
is missing.
