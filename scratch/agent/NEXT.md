# NEXT work unit — identify the port-side zero-payload source writer

HYPOTHESIS-ID: m5-output-source-writer

Session 3538 completed the batched output writer/order table. Retail passed
the whole-RDRAM control, reached title 1024 and hangar 512, and wrote
nonzero PCM bytes. The real-audio port reached both phases with live source,
consumer, image-stage, and completion controls; all sampled output writes
were RSP DMA rows with zero source and destination payloads, there were zero
guest/CPU writer rows, and joins were stage-only with no ordering violation.
See `docs/M5-S3538-OUTPUT-WRITER.md`.

Next unit: add one phase-keyed producer census immediately upstream of the
zero RSP source. Cover every CPU/RSP/host write into the image-task source
DMEM ranges and the PCM source state, and join each row to the existing
`audtask-image-stage`, source-DMA, completion, PCM-source, and PCM-consumer
ordinals. Keep the retail PCs `0x800078EC`, `0x80018F5C`, and `0x80018F60` as
attribution anchors only.

Competing hypotheses and discriminator:

- `H-PortSourceAbsent`: no legitimate producer reaches the source before the
  RSP DMA; select the first missing producer edge.
- `H-PortSourceZeroed`: a producer runs but writes zero before the DMA; select
  its writer PC and source value.
- `H-PortSourceOverwritten`: a nonzero producer runs, then a later clear
  zeroes the source; select the ordered writer/clear pair.
- `H-CaptureInvalid`: a positive control or target-phase join is absent.

The discriminating table is one run: phase, source address/range, writer
kind/PC, pre/post hash and nonzero count, RSP-DMA event, and nearest consumer.
A missing producer selects `H-PortSourceAbsent`; nonzero-then-zero selects
`H-PortSourceOverwritten`; a live zero-valued producer selects
`H-PortSourceZeroed`; failed controls select `H-CaptureInvalid`.

Exact starting commands:

    rg -n "audtask-image-stage|pcm-boundary|pcm-writer|DMA|memset|memcpy" src/main tools --glob '!**/*.log'
    cmake --build build -j8

Run one real-audio LLE/spin-yield/autopilot capture with the independent
retail controls. Do not change output state or copy retail bytes.
