# Next work unit (s4381): join named writer values to task ordinals

HYPOTHESIS-ID: m5-selector-decode-boundary

Competing hypotheses:

- H-post-publication-overwrite: the observed post-publication stores write
  payload values that replace or alter the just-published task payload.
- H-post-publication-maintenance: the stores are later maintenance traffic;
  their values do not overlap the published payload fields.
- H-value-watch-boundary: the range ordinal is real, but the post-store value
  and task snapshot are not sampled at the same writer event.

Discriminating measurement: in one qualified retail-oracle run, retain the
same `0x178C80:0x179A48` and `0x1E2FC0:0x1E3300` watches, typed
`0x80033FCC` task rows, three VI buckets, and scalar capture for
`0x8008F7D4`/`0x80091374`; extend the ordinal table so every retained write
also carries writer PC, exact destination, scalar source value, and nearest
task ordinal. A named-writer scalar store into a published payload field after
the same task selects H-post-publication-overwrite; named-writer stores after
publication but outside the task's published field set select
H-post-publication-maintenance; missing writer-keyed rows despite the existing
range hits selects H-writer-join-boundary. Require the whole-RDRAM positive
control, all three phase buckets, at least 1,000 valid type-2 rows, zero
ordinal overflow, and mismatch=0 for every interpreted scalar sample.

Ground-truth preflight: the oracle README says physical watches are independent
retail evidence, Rice plus the documented press schedule reaches title and
hangar, and `post-store-scalar` must report mismatch=0 before a scalar sample
is evidence. A failed positive control or missing phase/task coverage invalidates
the run rather than selecting a hypothesis.

Commands:

    bash tools/oracle/build.sh
    zsh scratch/agent/run_s4381_m5_writer_task_join.sh

Keep the oracle-only route; do not build the port or repeat the caller census,
direct publication join, first-eight comparison, or `0x8009C904:0x8009DC3C`
range.
