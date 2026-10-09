# Next work unit (s4380): identify values written after publication

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
`0x80033FCC` task rows, three VI buckets, and ordinal join; add post-value
capture for both ranges and writer PCs `0x8008F7D4` and `0x80091374`. A
phase-matched post-write value that equals or changes a published payload
word after the nearest task selects H-post-publication-overwrite; nonoverlap
with live post-publication stores selects H-post-publication-maintenance; a
missing same-event value row selects H-value-watch-boundary. Require the
whole-RDRAM positive control, at least 1,000 valid type-2 rows, zero ordinal
overflow, and nonzero post-write samples before interpreting a null.

Commands:

    bash tools/oracle/build.sh
    zsh scratch/agent/run_s4380_m5_payload_value_join.sh

Keep the oracle-only route; do not build the port or repeat the caller census,
direct publication join, first-eight comparison, or `0x8009C904:0x8009DC3C`
range.
