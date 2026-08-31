# M5 Session 3465 — retail table-load boundary

The independent Rice oracle ran one 90-second capture with the validated Start
schedule, title phase gates at `0x00790400` and `0x00790800` (width 1024), a
whole-RDRAM positive control, and the physical source watch at
`0x001E8710`. Execution watches covered `0x800644A8`, `0x800644DC`, and
`0x80064524`; post-store values were retained for the shared writer.

The controls were positive: whole-RDRAM recorded 12,666 callbacks and the
physical source watch recorded 2,666. Title-gated execution totals were 3,971
at `0x800644A8`, 16,905 at `0x800644DC`, and 16,745 at `0x80064524`.
The `0x800644DC` watch consistently had predecessor `0x800644D4`, and the
shared writer had predecessor `0x80064520`.

At the table-load site, retail's `v1` values identify entries such as
`0x801B4AA0`, `0x801B4AA8`, and `0x801B4B20`. The corresponding shared-writer
rows carry nonzero `s0` values including `0x801B4F00`, `0x801B4EC0`, and
`0x801B5E70`; the first comparable qualified port writer rows remain zero.
The retail post-store table independently measured 617 nonzero samples at
`0x80064524`, while `0x800644B0` remained 101/101 zero in this run.

This selects `H-TableEntryDivergence`: the value emerging from the retail table
walk differs from the qualified port value at the shared writer. It rules out
an absent retail load, absent shared writer, and failed observation controls at
this scope. It does not identify whether the port's table pointer differs or
which instruction writes the table entry, because this was a retail-only load
capture and the execution watch reports pre-load registers. The next probe
must attribute the source-table entry writer and join its value to the
`0x800644DC`/`0x80064524` rows.

Evidence: `scratch/agent/s3465_m5_retail_table_load/oracle.log` and
`scratch/agent/s3465_m5_retail_table_load/rc.txt`.

ORIGIN: the nonzero values are legitimate retail state pointers observed at
the shared writer and post-store watch; no mitigation or runtime behavior
change was added.
