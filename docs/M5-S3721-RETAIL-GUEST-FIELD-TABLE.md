# M5 s3721 — retail guest field table

The independent retail oracle ran with the whole-RDRAM positive control and
the `0x006AB400:512` hangar phase gate. The control reached 10,000 writes and
the run reached the 512-wide hangar phase. All four execution watches fired;
field-table rows were captured for `0x80033FCC` (4 distinct rows),
`0x80029E80` (464), and `0x80029F30` (464), while `0x80094648` executed 128
times but produced zero field rows.

The `0x80029E80` and `0x80029F30` rows shared the same state and field shape
(`s0=0x801496B0`, `s1=0`, `source_byte=0x7C`, `branch_state=0x10`) while
`0x80033FCC` used a distinct tuple (`s0=0x80128C70`, `s1=1`). Therefore the
retail guest paths are neither uniformly distinct nor uniformly aliased. The
`0x80094648` field capture is unevaluable despite its positive execution
watch. This narrows the next boundary to why the last path's field dumper is
empty and whether the two aliased paths intentionally share state.

ORIGIN: diagnostic-only oracle execution watches and field dumps. No guest or
host behavior was changed.

Evidence: `scratch/agent/oracle_s3721_retail_guest_fields/oracle.log`.
