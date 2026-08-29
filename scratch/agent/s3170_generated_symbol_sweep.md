# Session 3170 — generated-symbol sweep `0x800D0000..0x800E0000`

The bounded regeneration-safe sweep was run with the required changed-reference
control. The companion census classified `0x800D0120` and `0x800D03D0` as
ambiguous-or-fake. All other selected records were already synchronized,
including four existing duplicate-prefix mappings. The helper changed zero
references in zero files and returned its expected no-rename error under
`--require-rename`. An independent generated-definition search returned no
placeholder definitions in the interval.

This selects `H-Ambiguous` for the two unresolved records and
`H-Synchronized` for the rest. No semantic rename is justified in this band;
ambiguous records remain untouched. No build or game run was performed.
