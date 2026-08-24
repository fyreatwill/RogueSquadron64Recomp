# NEXT work unit (s2331) — M5 task output-metadata contract join

HYPOTHESIS-ID: m5-output-metadata-contract

## Work unit

Run one ground-truth-first, no-behavior-change join of every nonzero target
image stage to its task ABI metadata, all generated DMA ranges, image
completion, PCM source/consumer rows, host-boundary rows, and lifecycle rows.
Run the silent control and qualified Factor 5 image arm with
`ROGUESQ_DRAIN_INLOOP_TICK=1`. Do not add writeback, address remapping, slot
values, guards, or defaults. The s2329 destination-role result is
capture-dependent; do not repeat a destination census without the metadata
fields below.

## Competing hypotheses and discriminating measurement

- H-OutputBuffZero: the target image tasks advertise no output buffer, so the
  generated destination is not connected to the game-facing output contract.
- H-DataPtrRole: the task's `data_ptr`/`data_size` or a DMA range carries the
  role metadata, while `output_buff` is intentionally unused; destination role
  should follow that range/overlap classification.
- H-PCMPathOnly: task metadata and image DMA are valid, but only the host PCM
  path consumes the output; the missing slot/key-on rows remain a separate
  prior-route lifecycle issue.
- H-CoverageInvalid: the oracle, title/hangar route, task ABI/DMA, image
  completion, PCM, or guest-receive controls do not qualify the table.

The discriminator is one table keyed by `(arm, phase, origin, audio ordinal,
row, task n/begin/end, data_ptr/data_size, output_buff/output_buff_size,
every DMA range and its output/yield/data overlap, stage destination/length/
hash/nz, image completion, image classification, PCM source/consumer and
host-boundary range, same-ordinal/post-stage/prior lifecycle kind and signed
delta)`. Select H-OutputBuffZero only if every qualified nonzero target stage
has zero `output_buff`/size and no output-overlap range while image/PCM/route
controls are positive. Select H-DataPtrRole only if the nonzero destinations
partition by a nonzero data/output overlap or metadata role. Select
H-PCMPathOnly only if output metadata is valid and exact PCM joins exist but
the post-stage lifecycle remains absent while only prior-route rows remain.
Any missing positive control selects H-CoverageInvalid; filter/voice absence
stays unevaluable without its positive control.

## Exact commands

Create `scratch/agent/run_s2331_m5_output_metadata_join.sh` with a retail
oracle preflight first. Keep the whole-RDRAM positive control, the
`0x00165000:0x0016B000` physical destination watch, task/output/gate/wait/
status watches, title/hangar origins, named task/output writer PCs, and the
eleven-Start schedule. Require the same controls in the two port arms plus
`[audtask-abi]`, `[audtask-dma-row]`, `[audtask-dma-range]`, image-stage and
image-join rows in the image arm, guest-receive SP routes, and PCM
source/consumer rows in both arms. Use SIGKILL cleanup and leave the
filter/voice null unevaluable.

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh -n scratch/agent/run_s2331_m5_output_metadata_join.sh
    zsh scratch/agent/run_s2331_m5_output_metadata_join.sh s2331_m5_output_metadata_join
