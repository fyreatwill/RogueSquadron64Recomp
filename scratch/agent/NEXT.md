# Next work unit (s4385): compare actual hangar writer values to task payload

HYPOTHESIS-ID: m5-selector-decode-boundary

Competing hypotheses:

- H-hangar-selector-writer: actual hangar range-1 writer values recur in the
  phase-matched published task payload after publication.
- H-hangar-maintenance: writers are live and scalar-valid but have no
  phase/task-keyed payload equality.
- H-hangar-value-watch-gap: requested writer rows are absent or scalar
  validation is unsupported/mismatched.

Discriminating measurement: rerun the qualified s4384 oracle with
`--post-value-pc-detail`, retain task publication event rows, and make one
phase/task-keyed table joining each requested writer post-value to the nearest
type-2 task payload. A nonzero exact payload equality after publication selects
H-hangar-selector-writer; live scalar-valid rows with zero equality select
H-hangar-maintenance; absent/unsupported/mismatched requested rows select
H-hangar-value-watch-gap. Require the whole-RDRAM positive control, all three
buckets, at least 1,000 valid type-2 rows, zero ordinal overflow, and
`mismatch=0` for every retained scalar row.

Ground-truth preflight: use the independent retail oracle and preserve every
s4383 physical watch and phase schedule. Extract candidates with:

    rg 'ordinal-writer-join phase=0x006ab400:512 .*watch=1' scratch/agent/s4383_m5_writer_task_join_full/oracle.log | sort

Then create one self-contained runner from
`scratch/agent/run_s4384_m5_hangar_writer_qualification.sh`, changing only
the output directory and adding `--post-value-pc-detail`, and run it after:

    bash tools/oracle/build.sh

Do not repeat the caller census, first-eight comparison, or C904 range.
