# M5 Session 3408 — port boundary oracle

The retail oracle ran for 60 seconds with a whole-RDRAM positive control,
title/hangar VI gates, target-span watches, post-store sampling, and an
execution watch at `0x800052C4`.

The positive control reached 10,000 callbacks, and the run reached title 1024
and hangar 512. `0x800052C4` executed 3,728 times overall. Phase-gated counts
were 1,274 at origin `0x006AB400` and 1,663 at `0x006AB800`; its only observed
predecessor was `0x800052C0`. The target-span writer census was live in both
hangar buckets and included nonzero post-store payloads, but `0x800052C4` was
not itself reported as a target-span store PC.

Together with s3407's port witness (hangar image rows dominated by callsite
`0x800052C4`, with no `0x8002BEEC` or `0x800078EC` rows), this selects
`H-PortBoundaryDifferent`: the port's `0x800052C4` route is a distinct
translated producer boundary from retail's indirect `0x8002BEEC ->
0x800078EC` edge. It refutes the claim that a matching retail boundary is
absent. Causality from `0x800052C4` to the target payload remains open because
the oracle execution watch and target-span writer watch are not joined.

Evidence: `scratch/agent/s3408_m5_boundary_oracle_run3/oracle.log`.
