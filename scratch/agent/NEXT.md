# Next work unit: identify the writer that makes the input payload zero

HYPOTHESIS-ID: m5-input-payload-writer

S3691 selected `H-StaleInputPayload`: all 512 qualified hangar source rows
had equal zero input-DMA, source-RDRAM, and post-DMA DMEM payload fields, and
the input/source task-data pointers matched. The next unit is one
phase-scoped writer/descriptor boundary instrument and one qualified capture.

Competing hypotheses:

- `H-InputWriterZero`: a legitimate game writer zeroes `0x1797B0..0x179930`
  before the input DMA.
- `H-InputDescriptorWrong`: the task descriptor selects a distinct zero-filled
  source range or stale descriptor rather than the visible source witness.
- `H-PreDmaHostClear`: the port clears the source range before input DMA.

Discriminating measurement: one table for every title positive-control and
hangar input-DMA row, joining the immediately preceding writer PC/value or
descriptor source/length to the input-DMA row. A retail writer attribution
matching the port selects `H-InputWriterZero`; a descriptor/range mismatch
selects `H-InputDescriptorWrong`; a port-only clear with no retail counterpart
selects `H-PreDmaHostClear`. Missing whole-RDRAM positive control or missing
title nonzero rows is unevaluable.

Before building, obtain retail ground truth with the existing whole-RDRAM,
descriptor, source-span, title, hangar, and type-2 controls. Then batch the
writer/descriptor instrumentation into one build and run both real-audio and
silent arms together. Kill both game processes with SIGKILL and run from
`build/`.

Required commands once the instrument is written:

    ./submodule-patches/export.sh
    cmake --build build -j8
    env zsh scratch/agent/run_s3691_m5_input_payload_writer.sh
