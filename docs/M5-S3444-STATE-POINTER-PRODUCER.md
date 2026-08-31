# M5 s3444 — state-pointer producer census

The independent retail arm ran first with whole-RDRAM positive control,
target title origins `0x00790400`/`0x00790800`, hangar origin
`0x006AB400`, and the `0x80001CB8`/`0x80001CC8` execution watches. The
control reached 10,000 callbacks and the phase-gated field dump fired. In
the hangar buckets, the retail consumer's `s1=0x80194B20` rows contained
different source words and branch states at both 512 origins.

The fresh-build port pair was run concurrently. The first image arm hit the
known pre-title scheduler crash at guest PC `0x8000834C`, so that attempt was
not used. The immediate retry qualified both arms through title 1024 and
hangar 512, with consumer and output positive controls live, 512 consumer
rows and 343 output rows per arm, and no crash or abort markers. Silent and
Factor 5 image matched each other: the `0x80001CB8` consumer used state
addresses in `0x801BBD..`, observed `state_word=0`, and the first output use
at `0x80001CC8` was consistently `0x2`.

This selects `H-PortStatePointerGap` at the observed first-output boundary:
the port consumer is live, but its state-pointer family and pointed word do
not match the retail `s1=0x80194B20` family. It refutes parity at this
boundary and the prior value-join unevaluable hypothesis. It does not identify
the first writer/producer of the retail state pointer, and it does not prove
message zero is corrupt. No waits, slots, dispatch, clear behavior, or PCM
writeback changed.

Evidence: `scratch/agent/s3444_m5_state_pointer/oracle/oracle.log` and the
paired logs in `scratch/agent/s3442_m5_frequency_output_pair/`.
