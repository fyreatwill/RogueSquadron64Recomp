# M5 s3445 — state-pointer entry boundary

The independent retail arm passed its whole-RDRAM control and target phase
controls; the target field dump showed the retail `s1=0x80194B20` family.

The fresh-build silent and Factor 5 image arms both reached hangar 512 without
crash or abort. The existing consumer control and the new entry witness each
fired 512 rows per arm. In both arms, `rs_free` entered the target route with
`s1=0x80194B20`, pointed word `0x80194B40`, and `a0=0x801BEEB0`.

The same arms' post-receive consumer rows later exposed `0x801Bxxxx` state
pointers and output `0x2`. This selects `H-PortStatePointerClobber` between
`rs_free` entry and `0x80001CB8`, and refutes a missing upstream producer at
the entry boundary. The generated host wrapper still reports `ra=0`, so the
exact clobbering call remains open. No runtime behavior changed.

Evidence: `scratch/agent/s3445_m5_state_pointer_producer/port/{silent,image}.log`
and the independent capture in `oracle_fixed.log`. The first broad-range
capture remains separately as an unevaluable raw diagnostic artifact.
