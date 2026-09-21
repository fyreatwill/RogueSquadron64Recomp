# M5 Session 3666 — selector publication explains interleaved hangar objects

The corrected oracle capture used a whole-RDRAM positive control, four
descriptor watches, execution watches for `0x80033FCC`, `0x80090DE4`,
`0x80091060`, and `0x80091074`, four phase buckets, and a phase-gated task
dump. It ran 55 seconds to 3,280 VI and passed all controls: 322,682
whole-RDRAM writes, all four descriptor ranges, both title origins, both
hangar origins, and 1,878 valid type-2 task rows. There were no invalid task
pointers or dump overflows.

The selector and task streams agree row-for-row in execution order:

| VI origin | selector publication | task data pointer | rows |
|---|---|---|---:|
| `0x00790400` | `0x80173B20` | `0x80173B20` | 628 |
| `0x00790800` | `0x80171CE0` | `0x80171CE0` | 628 |
| `0x006AB400` | `0x80171E70` | `0x80171E70` | 253 |
| `0x006AB400` | `0x80173CB0` | `0x80173CB0` | 63 |
| `0x006AB800` | `0x80171E70` | `0x80171E70` | 63 |
| `0x006AB800` | `0x80173CB0` | `0x80173CB0` | 243 |

The selector/source changes with the alternating hangar object and is
published immediately before its corresponding task row. The writer census
still has a shared dominant caller `prev_pc=0x80090DE0`, with most rows
returning to `0x80090ABC`; the minor `0x80090BB4` variant does not define a
separate object producer in this capture.

This selects `H-SelectorInterleave`, refutes stable-selector downstream
switching, and leaves payload writer and exact DMA ordering open. The evidence
is single-source retail oracle data, with two independent phase-gated streams
(selector publication and task descriptor) joined in the same run.

ORIGIN: diagnostic-only selector/task/caller observations; no selector, task,
audio, descriptor, or output state was rewritten, skipped, or guarded.

Evidence: `scratch/agent/s3666_m5_hangar_selector_join/oracle.log`.
