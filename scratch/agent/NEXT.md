# Next work unit (s4387): census actual hangar payload writers

HYPOTHESIS-ID: m5-selector-decode-boundary

Competing hypotheses:

- H-actual-hangar-writer: a phase-512 writer PC outside
  `0x8008F7D4,0x80091374` writes the published hangar payload range.
- H-hangar-other-range: the named writers remain live in hangar but write a
  different destination range; the observed payload range is maintenance or a
  separate producer.
- H-value-watch-gap: the phase-512 writer/destination census is incomplete or
  unsupported.

Discriminating measurement: one retail-oracle run with the same whole-RDRAM,
VI phase, task, and ordinal controls, plus a phase-keyed writer-PC histogram
for payload range `0x178C80:0x179A48` and a bounded exact writer table in the
hangar bucket. Compare the complete phase-512 writer PCs and destinations
against the named writers. A new high-volume writer selects H-actual-hangar-
writer; live named writers with no range-1 stores and a different phase-512
destination select H-hangar-other-range; absent/unsupported/overflowed rows
select H-value-watch-gap.

Controls required: whole-RDRAM positive control, title origins
`0x00790400:1024` and `0x00790800:1024`, hangar origin `0x006AB400:512`, at
least 1,000 valid type-2 rows, zero ordinal overflow, and `mismatch=0` for the
requested scalar writers. Do not repeat the stale detail list or interpret
ordinal `equal` as payload equality.

Exact commands:

    bash tools/oracle/build.sh
    create scratch/agent/run_s4387_m5_hangar_writer_census.sh from the s4386
    runner, replacing the detail arm with phase-512 writer/destination census
    options
    bash scratch/agent/run_s4387_m5_hangar_writer_census.sh

Summarize only bounded `rg`/`sed` windows from the oracle log.
