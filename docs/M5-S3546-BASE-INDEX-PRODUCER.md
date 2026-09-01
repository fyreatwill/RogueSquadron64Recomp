# M5 session 3546 — base/index producer boundary

The batched witness covered `loadTextureToMemory` entry `0x8001F954`, table
base reload `0x8001FA64`/`0x8001FAB4`, index formation `0x8001FAA0`, and the
combined pointer at `0x8001FAC4`. The independent retail arm watched the same
PCs and included a whole-RDRAM positive control; the port arm used the same
real-audio LLE/spin-yield/autopilot route as the validated baseline.

Controls were live: retail recorded 10,674 whole-RDRAM writes and 674 writes
in `0x1797B0:0x179930`; both arms reached title VI 1024 and hangar VI 512.
The port producer control fired in both phases, with 128 rows per stage in
each target phase before its 512-row phase cap.

In hangar, retail and port both executed the shared family with
`a0=0x8016BCA0`, `a1=0x8003B6E0`, `a2=0x10`, and `s3=0x2004`. Retail's
index-formation rows began with index `0x37` and then `0x39`; the port rows
began with `0x25` and then `0x27`. Their stage-P record pointers consequently
also differed. The first observed divergence is therefore in the producer
state/index before the scalar texture-record stores, selecting
`H-ProducerDivergence` and ruling out a store/writeback explanation at this
boundary.

This is two-source evidence, but the independent runs are not ordinally
joined; the shared input tuple and repeated stage shape are the comparison
key. The next boundary is the retail predecessor `0x80022ACC` and its port
caller/input equivalent.

ORIGIN: the texture-record writes are legitimate game operations; this
instrument only observes the upstream producer and changes no game state.

Evidence: `scratch/agent/s3546_m5_base_index_producer/oracle.log`,
`scratch/agent/s3546_m5_base_index_producer/port.log`, and
`scratch/agent/retail_preclear_groundtruth.log`.
