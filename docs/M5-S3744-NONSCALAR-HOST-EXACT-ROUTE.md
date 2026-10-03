# M5 session 3744 — non-scalar and host exact-route census

The retail oracle passed the whole-RDRAM positive control (10,010 writes) and
reached both target buckets: 632 title VIs and 543 hangar VIs. Exact physical
watch `0x128C92` had zero writes. `0x128CD0..0x128CD3` had five writes, with
the writer histogram identifying retail PC `0x8001BB14`.

The qualified port reached title `1024 @ 0x00790400` at 14.3s and hangar
`512 @ 0x006AB400` at 23.5s. The exact generated-store witness and new DMA
witness passed positive controls; both had zero target rows. The all-generated-
store census passed controls and emitted 512 phase-scoped neighboring rows
from `0x8001A06C/74` and `0x8001C21C/24`, all zero-valued, with no exact-field
row. A concurrent real/silent attempt was invalid because both arms stalled at
early 640 before either target phase.

This closes the measured port generated scalar, non-literal generated-store,
and RSP-DMA writer classes. Arbitrary host-side RDRAM writes remain open. No
mitigation is justified.

ORIGIN: the retail exact-field writer is `0x8001BB14`; the observed port
writers are legitimate zero-valued neighboring route-state stores. This
iteration adds witnesses only; it does not suppress or rewrite either value.

Evidence: `scratch/agent/s3744_oracle_groundtruth/clean/oracle.log`,
`scratch/agent/s3744_port_exact_route/qualified-real/real.log`, and
`scratch/agent/s3744_port_exact_route/qualified-real-allstores/real.log`.
