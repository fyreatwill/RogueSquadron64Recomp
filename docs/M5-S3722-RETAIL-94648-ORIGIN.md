# M5 s3722 — retail `0x80094648` origin boundary

Ran the independent retail oracle with the whole-RDRAM positive control, both
512-wide VI origins, the four execution watches, and a field dump for all four
PCs. The first invocation was invalid because `--pc-field-dump-any-phase` is a
flag; the corrected invocation placed `0x80094648` in the field-dump PC list
and then enabled that flag. The corrected run exited `rc=0`.

The positive control reached 10,000 writes. The run reached both target
origins, `0x006AB400` and `0x006AB800`, at width 512. The `0x80094648`
execution watch fired, and its field dumper produced 128 rows. Every one of
those rows had origin `0x006AB800`, with changing `s1`/pointer fields and
`source_byte=0x00`; there were no `0x80094648` field rows at `0x006AB400`.

This selects `H-Retail94648-OriginMismatch`: the previous empty table was
caused by an overly narrow origin gate, not by an unsupported field capture.
It refutes `H-Retail94648-FieldUnsupported` for the measured second origin and
refutes `H-Retail94648-PreTargetOnly` because `0x006AB800` is the target
512-wide phase. This is single-source independent-retail evidence; it does
not yet explain whether the `0x80029E80`/`0x80029F30` shared tuple is
intentional.

Evidence: `scratch/agent/oracle_s3722_retail_94648_fields/oracle.log`.

ORIGIN: diagnostic-only oracle execution watches and field dumps. No guest or
host behavior was changed.
