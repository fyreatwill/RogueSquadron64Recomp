# M5 session 3552 — cached-head branch was not taken

The regeneration-safe heap table was run on the canonical real-audio,
LLE-solo, spin-yield/autopilot route after a first attempt stalled at VI 640.
The fixed retry added the qualified `ROGUESQ_M5_C88_VALUE=0` route aid and
used the successful eight-event schedule.

The retry passed the same-run controls: it emitted the autopilot arm and six
fires, then reached title VI `0x00790400` (1024) and hangar VI `0x006AB400`
(512). The heap entry witness emitted 96 rows across the target phases. The
cached-head pre-store witness emitted zero rows; there was no crash marker
before deliberate SIGKILL.

This selects `H-HeapPathAbsent`: entry activity does not imply that the
`0x8000D700` branch was taken, and this run gives no evidence that the cached
head is corrupt. The next discriminator is a phase-scoped caller/route table
at the two known generated edges, `0x800104A8` and `0x80010CD8`, joined to the
existing entry witness. This is single-source port evidence; no retail writer
or branch-equivalence evidence was collected in this unit.

ORIGIN: diagnostic-only observation; no mitigation or heap/audio write changed.
