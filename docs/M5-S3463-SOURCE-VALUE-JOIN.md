# M5 Session 3463 — port and retail source-value join

The qualified port capture and independent retail oracle were joined at title
origin `0x00790400`, phase 4, by writer PC and per-PC ordinal. Both runs had
positive controls: the port emitted 1,024 title source rows, while the retail
oracle recorded 12,734 whole-RDRAM callbacks, 2,734 physical source-watch
writes, and 633 title VI frames.

At `0x800644B0`, the first 768 comparable rows match exactly: both write
`0x00000000`. At `0x80064524`, the writer PC also matches, but the first
comparable row diverges: port writes `0x00000000`, while retail writes
`0x801B4F00`. The port has 256 rows at this PC and retail has 316; the
additional retail tail is not needed for the first divergence.

This selects `H-FirstValueDivergence`: the missing contract is upstream of the
value presented to the shared `0x80064524` writer, not a writer-route change.
The retail value is legitimate at this scope because it is an immediate
post-store observation under the independent physical watch. The next probe
must identify the writer or producer that supplies the nonzero retail value;
do not change audio waits, slots, dispatch, clear behavior, or PCM writeback.

Evidence: `scratch/agent/s3461_m5_source_value_join/run.log` and
`scratch/agent/s3462_m5_retail_ordered_source/oracle.log`.
