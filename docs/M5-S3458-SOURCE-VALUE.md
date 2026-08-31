# M5 Session 3458 — source-slot writer values

The retail oracle ran with a whole-RDRAM positive control, the physical source
watch at `0x001E8710:0x001E8714`, the title phase gate, and post-store sampling.
The control recorded 11,198 callbacks and the source watch recorded 1,198
writes. Title reached origin `0x00790400` for 233 VI. Post-store samples were:
`0x800644B0` 807 zero / 0 nonzero, `0x80064524` 0 / 269,
`0x800078EC` 18 / 14, `0x80018F5C` 0 / 1, `0x80018F80` 2 / 70,
`0x80028F90` 2 / 7, and `0x800C871C` 0 / 1. The sampled nonzero value
matching the producer witness was `0x801B4F00` (267 samples).

The matching port binary was rebuilt. The first attempt omitted the required
spin-yield/LLE route and stayed at 640. The fixed attempt included
`ROGUESQ_LLE_FORCE=1`, `ROGUESQ_LLE_UNGATED=1`, `ROGUESQ_LLE_SOLO=1`, and
`ROGUESQ_SPIN_YIELD=1`, but crashed in `spTaskSchedulerThread` with SIGBUS at
guest PC `0x8000834C` before title; it emitted zero source-value rows. The
port control therefore failed and the retail values cannot yet be joined to a
port writer in this session.

The retail result is single-source evidence for value legitimacy. It selects
that the shared and retail-only writers do not all store the same value, but
does not select `H-RetailValue` versus `H-SharedValue` versus `H-PortValue`
until the port reaches the same title phase. The fixed-route crash is a route
qualification defect, not evidence about the audio output contract.

ORIGIN: the observed values are written by the named guest scalar-store PCs;
the nonzero source-slot values are legitimate retail state values because they
are observed directly after the stores, but their port-equivalent route is
unqualified.

Evidence: `scratch/agent/s3458_m5_source_value/oracle_retry.log`,
`scratch/agent/s3458_m5_source_value/port_fixed/run.log`.
