# M5 Session 3668 — pre-selector writer context join

The independent retail oracle passed the whole-RDRAM positive control, all
four descriptor watches, title VI `0x00790400`, hangar VI `0x006AB400`, and
the type-2 task control. The fixed capture ran 50.6 emulated seconds and
recorded 299,080 whole-RDRAM writes, 674 writes to
`0x1797B0..0x179930`, and 822 valid type-2 task rows with zero invalid
pointers or overflow.

The bounded field-context arms for the smaller source-writer sites joined
title rows to task data `0x80173B20` and hangar rows to `0x80173CB0`:
`0x8001FADC`, `0x8001FAE4`, `0x8001FAEC`, `0x8001FAF0`, `0x8001FB10`, and
`0x8001FB14` each produced 217 title joins and 203 hangar joins. The
`0x8001FBE4` site produced 13 title and 11 hangar joins. The field rows did
not join the alternate `0x80171CE0`/`0x80171E70` objects, and the joins are
latest-task-per-VI-bucket joins rather than exact store-to-task edges.

This selects a limited `H-PreSelectorObjectWriter` result for the observed
smaller writer family: its phase-gated context follows the selected object
family (`0x80173B20` in title and `0x80173CB0` in hangar). It does not resolve
the primary `0x800078EC` writer or prove ownership of the alternating
`0x80171CE0`/`0x80171E70` objects. The first attempt was capture-invalid
because dumping `0x800078EC` field rows produced 1,404,783 hits and reduced
the run to 30 emulated seconds; removing only that high-cardinality dump
allowed the fixed run to reach hangar. This is single-source retail evidence.

ORIGIN: diagnostic-only oracle execution, field, task, descriptor, and
physical-write watches; no guest or host state was rewritten, skipped, or
guarded.

Evidence: `scratch/agent/s3668_m5_preselector_writer_join/oracle.log`,
`scratch/agent/run_s3668_m5_preselector_writer_join.sh`, and the independent
oracle controls described above.
