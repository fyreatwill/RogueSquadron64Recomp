# NEXT work unit — join the port 0x800052C4 route to its target payload

HYPOTHESIS-ID: m5-port-052c4-payload-join

Session 3408's oracle positive control passed and reached both hangar origins.
Retail executed `0x800052C4` 1,274 times at `0x006AB400` and 1,663 times at
`0x006AB800`; target-span stores were nonzero in those same buckets. Session
3407's port image rows were dominated by `0x800052C4`, but the host witness
did not join that callsite to its downstream store.

Competing hypotheses:

- `H-Port052C4Publishes`: the port `0x800052C4` route reaches the target
  publication and its zero payload is produced downstream of that call.
- `H-Port052C4Distinct`: the callsite is active but publishes a different
  structure; the zero PCM source has another producer gap.
- `H-Port052C4JoinGap`: the existing host witness cannot safely join this
  indirect route to its destination, so the result remains unevaluable.

Discriminator: batch one port build/run with a phase-scoped `0x800052C4`
call/return or destination join, plus whole-RDRAM, title/hangar, image/DMA,
and PCM positive controls. A call joined to the zero target publication selects
`H-Port052C4Publishes`; a live call with no target join but live independent
target stores selects `H-Port052C4Distinct`; a failed join with controls live
selects `H-Port052C4JoinGap`. Do not change waits, slots, dispatch, or PCM
writeback.

Use the existing qualified image/silent route and add only the join witness;
build once and run both arms in that same iteration. Preserve the oracle log
at `scratch/agent/s3408_m5_boundary_oracle_run3/oracle.log` as ground truth.
