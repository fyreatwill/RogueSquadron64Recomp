# s2672 M5 output/publication edge audit

## Scope and controls

This is a static audit of the qualified s2671 image-arm capture. The image
positive control is live in the same artifact: 987 `audtask-abi` rows, 2,132
DMA-range rows, 4,399 image-stage rows, 975 image-stage joins, `break_pc=0x1328`,
and `exit=1`. The paired silent arm has no image-stage rows, so the image work
is not a probe-only artifact. No runtime behavior, task field, gate, writeback,
remap, or guard changed.

## Discriminator table

The table collapses repeated rows only by the exact observed destination or
PCM-address class; counts cover every matching s2671 image-arm row.

| Observed class | Task/stage relation | Payload and writer evidence | MORT / PCM relation and ordering | Result |
| --- | --- | --- | --- | --- |
| `0x166450:0x169450`, rolling `0x300` stage-2 destinations | `field44` is the stage-2 destination; DMEM `0x6F0`, length `0x300`; 1,139 stage-2 observations | Almost all rows are `fnv=F59C39C5`, `nz=0`. The only nonzero image payloads are three rows at `0x166D50` (`nz=621`) and `0x167050` (`nz=639`) in one task. No `output_buff` overlap and no target-span `field348` writer row | PCM source/consumer rows use the same rotating `0x166xxx` addresses, but payload is zero except the matching one nonzero pair (`nz=621`). Joins show source-before-consumer and consumer-after-task, but no named MORT writer or stable image-completion-to-nonzero-publication contract | Destination overlap is real, but it does not identify a CPU MORT publication edge; `H-image-contract-edge` remains unclosed |
| `0x1798B0:0x179A48` | Stage 3: `r6` is incremented by `0x100` before the `0xCB0` / `0x198` writeback; in hangar `field348=0x801797B0`, so `dest=field348+0x100=0x801798B0` | 318 stage-3 DMA-range rows use `fnv=762B22A5`, `nz=0`; corresponding stage-3 image rows report zero destination payload. No field writer/candidate/memset row fired | No PCM source or consumer row uses `0x1798B0`; PCM rows are centered on `0x166xxx`. The retail audit classifies the same-span PCs (`0x800078EC`, `0x8001E2C0`, `0x8001FAxx–0x8001FD2C`) as memset/texture-record writers, not MORT output | `field348+0x100` is an image-task destination relation, not a demonstrated PCM publication edge; image and CPU-MORT hypotheses remain open |
| `0x178D80:0x178F18` | Stage-3 destination seen in title/non-hangar rows; same DMEM `0xCB0`, length `0x198`, but not hangar `field348+0x100` | 667 rows, `fnv=762B22A5`, `nz=0`; no output overlap and no named target-span writer | No matching PCM source/consumer address or MORT descriptor/order join | Unmapped image-side storage |
| `0x1935E0:0x193778` | Stage-3 destination seen in the title path; same `0xCB0` / `0x198` shape | One observed row, `fnv=762B22A5`, `nz=0`; no target-span writer | No matching PCM source/consumer row or MORT relation | Unmapped image-side storage |
| `0x178C80:0x178C88` | One 8-byte image DMA control/header row | One nonzero row (`fnv=07E44B4B`, `nz=4`); not a PCM-sized buffer and not in stage-2/3 spans | No PCM source/consumer match; no MORT descriptor or output-field relation | Control metadata, not a publication edge |
| PCM source and consumer rows at `0x166450` through the rotating `0x169xxx` ring | 1,190 source and 1,191 consumer rows; 384 samples / 768 bytes per row | `fnv=F59C39C5`, `nz=0` except one source/consumer pair at `0x166D50` with `nz=621`; host writer snapshot is `writer_pc=0`, `writer_value=0` and reports only zero-valued writes | Join layer proves source-before-consumer for 1,843 rows and consumer-after-task for 1,432 rows, but zero payload remains zero through consumer. No row identifies a CPU MORT writer, descriptor class, or nonzero completion publication | Live consumer path, unresolved producer/publication origin |
| Task ABI `data_ptr+0x100` | Sample task pointers include `0x80173CB0`, yielding `field_phys=0x173DB0`; other task data pointers resolve into their own task-data neighborhoods | All 987 ABI rows retain `output_buff=0`, `output_buff_size=0`, and `field_write_event=0`; no ABI field writer fired | Computed task-field address does not equal stage-2 ring or hangar stage-3 `0x1798B0` in sampled rows | `data_ptr+0x100` is not the missing edge in this capture |

## Verdict

`H-unmapped-edge` is selected. The image path has a legitimate, repeatable
task-to-DMA relation, and its stage-2 ring overlaps the host PCM address family,
but the only nonzero rows are an isolated pair and there is no named MORT
writer, nonzero payload publication, or complete task-completion-to-consumer
join. The stage-3 `field348+0x100` relation is real but points to a separate,
zero-valued image buffer; the independent retail writer audit identifies the
same secondary span as texture/image metadata activity. This rules out landing
writeback or an output remap from destination overlap alone.

The next discriminating work must obtain an independent writer/order mapping
for the rotating `0x166xxx` ring or a CPU-side MORT output callsite. Repeating
the existing task-field census or adding a broad writeback would not split the
remaining hypotheses.
