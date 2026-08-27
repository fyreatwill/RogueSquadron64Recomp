# NEXT work unit (s2655) — M5 dispatch-time OSTask output/DMA join

HYPOTHESIS-ID: m5-pcm-publication-edge

## Work unit

Run one phase-gated runtime capture of every image-arm `M_AUDTASK` task's
`output_buff` and `output_buff_size` at dispatch, joined to its generated DMA
ranges and payload nonzero counts. The s2654 static audit found no generated
OSTask construction site: `output_buff` is ABI offset `0x28`, size is `0x2C`,
and the five generated `osSpTaskStartGo` sites only dispatch queued task
pointers. Do not build a new instrument if the existing dispatch/DMA rows
already contain these fields; use the existing recipe and parser.

## Competing hypotheses and discriminator

- `H-OutputBuffNull`: dispatch rows show `output_buff=0` or size `0`; no DMA
  range overlaps a legitimate output buffer.
- `H-OutputBuffValid`: dispatch rows show a nonzero RDRAM pointer/size, and a
  DMA range overlaps it; any remaining gap is after the RSP write.
- `H-ImagePCMSilent`: the pointer is valid but all joined DMA payloads are
  zero, indicating silent image input/output rather than routing loss.
- `H-PortFuncMissing`: no qualifying image-arm dispatch row reaches a valid
  task/output contract, indicating the producer/submission path is absent or
  blocked.

The discriminator is the same task ordinal in one run: `output_buff`, size,
DMA destination overlap, DMA payload nonzero count, image exit, and PCM
source/consumer rows, separately for title `1024 @ 0x00790400` and hangar
`512 @ 0x006AB400`. A whole-RDRAM oracle control and port phase transitions
are required; a zero without those controls is unevaluable.

## Exact commands

1. Verify the existing image/default and silent arms are built from the same
   executable: `git status --short` and inspect the latest qualifying recipe
   under `scratch/agent/run_s2346_m5_task_output_provenance.sh`.
2. Run that recipe from the build directory with its existing
   `PROBE_PHASE_WIDTH=1`, `PROBE_KEYS_FROM_PHASE=1`, `ROGUESQ_LOG_ALL=1`, and
   passive breadcrumb variables. If the recipe is not self-contained, enqueue
   a self-contained wrapper under `scratch/agent/soak_queue/` instead of
   babysitting it.
3. Parse the image-arm rows with the recipe's existing parser. Report counts
   for ABI rows, DMA rows/ranges, nonzero joined payloads, output-buffer/DMA
   overlaps, image exits, PCM source/consumer rows, and both phase controls.

## Expected outcomes

- Nonzero `output_buff`/size plus an overlapping nonzero DMA payload selects
  `H-OutputBuffValid` and makes the next work unit the post-DMA PCM consumer
  edge.
- Zero pointer/size selects `H-OutputBuffNull` and makes the next unit trace
  the guest task producer/allocator; do not add writeback.
- Valid fields with zero payload selects `H-ImagePCMSilent`; next unit is the
  input/source population contract, not host routing.
- Missing qualifying dispatch rows selects `H-PortFuncMissing` only if the
  port route control is positive; otherwise the result is unevaluable.

Do not repeat the title-zero census, revisit `0x80094648`, or promote any
writeback/remap/guard without a named writer, legitimate value, and ordering.
