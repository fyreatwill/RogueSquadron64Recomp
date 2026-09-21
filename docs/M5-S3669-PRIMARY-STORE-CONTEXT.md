# M5 Session 3669 — primary pre-selector store context

The independent retail oracle ran the exact-store arm for `0x800078EC` against
source span `0x1797B0..0x179930`, while retaining the whole-RDRAM positive
control, all four descriptor watches, title/hangar phase watches, and the type-2
audio-task control.

Controls passed: `293,638` whole-RDRAM writes, `674` source-span writes,
nonzero writes in all four descriptor ranges, title VI `0x00790400`, hangar VI
`0x006AB400`, and `813` valid type-2 task rows with zero invalid pointers or
overflow. The run reached `3008` VI (`~50.1` emulated seconds).

The bounded store arm recorded `384` callbacks and `384` unique rows, with no
overflow. Every row was the same call context: guest `$a0=0x801797B0`, `$a1=0`,
`$a2=0x298`, `$ra=0x8008F2D4`, and execution PC `0x800078EC`. The changing
store address and aligned pre-store word reflect the byte loop and must not be
mistaken for changing source-object context.

This selects `H-PrimaryInitialization` for the primary writer: the observed
writer is a fixed zero-fill initializer, not an object-specific payload writer.
It is single-source retail evidence. It does not identify the remaining
`290` source-span writes or exact DMA ordering, so it does not close M5 Step 3.

ORIGIN: diagnostic-only oracle execution and physical-write watches; no guest
or host state was rewritten, skipped, or guarded.

Evidence: `scratch/agent/s3669_m5_primary_store_join/oracle.log` and
`scratch/agent/run_s3669_m5_primary_store_join.sh`.
