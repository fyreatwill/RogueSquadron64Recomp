# M5 Session 3665 — hangar task join is interleaved by buffer origin

The fixed oracle capture used a whole-RDRAM positive control, four descriptor
ranges, explicit execution watches for `0x80033FCC` and `0x80090DE4`, and
phase-gated joins for both title and hangar buffer origins. The initial
capture omitted `--watch-pc`; its zero task/field rows are an instrument setup
failure and are not evidence. The corrected finite run passed the positive
control (`275,347` whole-RDRAM writes), all four descriptor watches, and all
four target VI buckets. It produced `1,876` valid type-2 task rows and `2,656`
field rows with no invalid pointers or overflow.

Joined task data by VI origin:

| VI origin | joined task data pointers | joined rows |
|---|---|---:|
| `0x00790400` | `0x80171CE0` | 60 |
| `0x00790800` | `0x80173B20` | 60 |
| `0x006AB400` | `0x80171E70`, `0x80173CB0` | 87 |
| `0x006AB800` | `0x80171E70`, `0x80173CB0` | 96 |

The title mapping from s3664 reproduces, but each hangar 512 origin
interleaves both previously observed hangar task objects. The dominant field
caller remains `prev_pc=0x80090DE0`; most rows retain `$ra=0x80090ABC`, with a
minor `$ra=0x80090BB4` variant on the interleaved hangar rows. Thus a simple
one-task-per-VI-origin route rule is refuted. The shared caller family remains
supported, but universal logical ownership is not selected because the
hangar object alternation is still unexplained.

ORIGIN: diagnostic-only task/writer joins; no guest or host value was skipped,
rewritten, or guarded.
