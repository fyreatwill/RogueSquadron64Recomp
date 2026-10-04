# Next work unit: audit free-list/active-queue ownership aliasing

HYPOTHESIS-ID: m3-free-active-ownership-alias

The mandated no-churn pivot selects the next M3 guard-class change instead of
the queued M5 census. Audit `func_80007D74`'s ownership boundary: the current
patch checks that the popped node is absent from the active queue, but does not
check whether any remaining free-list node aliases that queue. Add one bounded
cross-chain disjointness check and return before link mutation on overlap.

Competing hypotheses:

- H1: free-list and active-queue ownership are intended to be disjoint, so a
  cross-chain alias is invalid and should be rejected before append stores.
- H2: the two chains may legitimately share nodes, so the new check would
  reject valid allocator state and must not be landed.
- H3: the patch pipeline is unavailable, so source-level guard work can land
  but runtime qualification remains blocked.

Discriminator: compile the patch source and attempt the configured
`PatchesLib` target. A successful patch build with the new guard selects H1
only if the source preserves the existing valid-link path; an unavailable
target selects H3. H2 would require independent evidence of intentional
cross-ownership, which is not present in the allocator contract.

Commands:

    cmake --build build --config Debug --target PatchesLib

Then inspect the target result and source diff. Do not run an M5 census or
repeat a soak in this iteration.
