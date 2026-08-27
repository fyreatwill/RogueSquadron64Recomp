# s2513 M5 image payload writer provenance

Date: 2026-08-26
Build: `cmake --build build --target RogueSquadron64Recomp` (passed)
Recipe: `run_s2513_m5_payload_writer.sh`, corrected with
`ROGUESQ_LOG_PCM_BOUNDARY=1` and `ROGUESQ_LOG_PCM_SANITY=1`.

The first attempt omitted the PCM-boundary gate and is unevaluable. The
corrected paired-image arm passed the required controls: AI-table 1/16 rows,
3,381 image-stage rows, 1,479 image-DMA joins, 3,783 task joins, 98 PCM
source/consumer pairs, and 1,024 PCM-writer rows. It recorded zero guest CPU
writer rows and zero second-range writer rows. The paired silent arm supplied
97 PCM source/consumer pairs and zero image-stage/writer rows, confirming the
consumer controls are live independently.

Image ordinal 606 produced stage-2 payload at `0x168B50`, length `0x300`, FNV
`2B9E9631`, with 621 nonzero bytes. A PCM source and consumer then used the
same address, FNV, and nonzero count. Writer observations were kind 2
image/DMA observations, not kind 1 CPU stores. This selects
`H-rsp-payload-writer` at the observable image-to-consumer boundary and rules
out `H-guest-payload-writer` and a fully controlled no-writer result.

Limitation: the lower-level `audtask-image-dma-join` rows reported zero
nonzero bytes for the corresponding DMA observer. Exact DMA-event attribution
therefore remains open; the stage-row plus independent PCM source/consumer
identity is the current two-line evidence. No mitigation or audio behavior
change was made.
