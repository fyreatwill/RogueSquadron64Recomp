# NEXT work unit (s2499) — audit the kind=2 PCM-ring writer provenance

HYPOTHESIS-ID: m5-generated-image-downstream-join

## Single work unit

Perform a bounded static census of every caller of `rs64_pcm_writer_note` and
the `kind=2` path in `src/main/main.cpp`, then trace the corresponding
`g_rs64_pcm_last_dma_phys` producer back to the image/audio callback boundary.
Use the existing s2498 rows as the starting address set; do not add runtime
fields or change behavior unless the census proves that the current writer
kind is misclassified.

## Competing hypotheses and discriminator

- H-kind2-generated: `kind=2` is the legitimate generated audio/image writer
  and can be joined to the nonzero PCM buffers by its DMA producer.
- H-kind2-host: `kind=2` is only a host-side DMA bookkeeping notification and
  is not a game-side PCM writer.
- H-kind2-unresolved: the static callers do not identify a legitimate writer
  or stable DMA-to-consumer relation.

The discriminator is one caller/producer table with caller PC, kind, DMA
source/destination/length, ring slot, and the first downstream consumer. A
complete producer-to-nonzero-consumer relation selects H-kind2-generated; a
host-only callback with no guest writer selects H-kind2-host; an unresolved
producer or ambiguous relation selects H-kind2-unresolved.

## Exact commands

```sh
rg -n "rs64_pcm_writer_note|g_rs64_pcm_last_dma_phys|queue_samples|kind=2|pcm_ring" src lib RecompiledFuncs
sed -n '300,530p' src/main/main.cpp
sed -n '3100,3190p' src/main/main.cpp
rg -n "rs64_pcm_writer_note|g_rs64_pcm_last_dma_phys" src lib RecompiledFuncs
```

Write the table and conclusion to
`scratch/agent/s2499_m5_kind2_writer_audit/audit.md`. No build is needed
unless the static census exposes a concrete missing caller or wrong kind.
