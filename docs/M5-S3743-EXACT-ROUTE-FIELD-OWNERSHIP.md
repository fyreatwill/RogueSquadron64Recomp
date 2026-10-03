# M5 session 3743 — exact route-field ownership

The retail oracle passed a whole-RDRAM positive control (21,643 hits) and
reached title `1024 @ 0x00790400` plus hangar `512 @ 0x006AB400`. Exact
physical watches at `0x128C92` and `0x128CD0..0x128CD4` had no target-phase
writes; the route-PC watches fired.

The port added a regeneration-friendly witness to generated stores using
literal route-object offsets `+0x22` and `+0x60` (379 sites in 43 files).
Its positive control fired in both arms. The qualified real-alone run reached
both target phases without a crash, recorded 512 neighboring route-span rows
all valued zero, and recorded zero exact-field rows. The silent arm also had
zero exact-field rows. The first paired attempt was invalid because the real
arm crashed before its target phase while two instances ran concurrently.

This selects `H-ExactFieldUnwritten` for the generated scalar store class and
adds independent retail evidence against an exact-field scalar writer. DMA,
host-side, and non-literal-address writes remain untested, so
`H-RouteStateNotSource` remains open and no mitigation is justified.

Evidence: `scratch/agent/s3743_oracle_groundtruth/oracle.log`,
`scratch/agent/s3743_m5_exact_route_ownership/real-alone.log`, and
`silent.log`.
