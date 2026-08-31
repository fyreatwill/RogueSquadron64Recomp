# M5 s3449 — title state tuple context

The retail oracle was run before the port with a whole-RDRAM write watch and
execution/field watches at `0x80001C98`, `0x80001CB8`, `0x80001CC8`, and
`0x80001F84`. The positive control reached its 10,000-callback cap, all four
execution watches fired, and the run completed 3,260 VI. Retail field rows
included title-phase state tuples in the `0x801Bxxxx` family; at
`0x80001CB8`, one row had `s0=0x801B95F0`, `s1=0x801B1590`, and source word
`0x00000008`.

The planned wrapper was missing, so an equivalent wrapper was restored as
`scratch/agent/run_s3449_m5_state_tuple_context.sh` and run after one clean
build. Its silent and Factor 5 image arms both reached title 1024 at origin
`0x790400`, each emitted 512 state-entry rows and 1,024 ordered checkpoint
rows, and each emitted 512 consumer rows and 343 output rows. Their first
state rows agreed: `s1=0x801B1590`, entry state `0x801B95F0`, followed by the
same pointer and state through post-receive and pre-consumer. The wrapper
return address remained zero in both arms.

This selects `H-StatePointerParity` for the observed title boundary and rules
out a port-only pointer clobber between entry, receive, and consumer. The
retail row independently contains the same `s1` and state-pointer tuple,
which is the second evidence line for that boundary. It does not identify why
the earlier `s1=0x80194B20` route differs, nor does it explain the downstream
output contract or the zero host-wrapper return address.
