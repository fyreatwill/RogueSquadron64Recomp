# NEXT work unit (s2505) — join the RSP image-output destination to the AI table

HYPOTHESIS-ID: m5-pcm-payload-writer-provenance

## Single work unit

Run one static join census over the image-arm RSP output path. Start at the
generated audio-task output/data fields and the RSP image-stage/DMA destination
records, then determine whether any path can equal `D_801496B0[i]` or
`D_801496B0 + n*0x300`. Do not use the superseded `0x801096B0` address. No
build, runtime fields, address remap, or behavior change.

## Competing hypotheses and discriminator

- `H-rsp-destination-joined`: the RSP image/output destination is provably one
  of the allocated AI blocks.
- `H-rsp-destination-distinct`: the image/output destination is provably not
  one of the allocated AI blocks.
- `H-rsp-destination-unresolved`: the available static fields do not preserve
  enough identity to decide.

The discriminator is a complete table keyed by task/output guest PC, image
ordinal, DMA destination/length, and AI-buffer derivation. Equality to a
derived AI block selects `H-rsp-destination-joined`; explicit inequality
selects `H-rsp-destination-distinct`; otherwise select
`H-rsp-destination-unresolved`.

## Exact commands

```sh
rg -n -i --glob '*.c' --glob '*.cpp' --glob '*.h' --glob '*.py' --glob '*.toml' --glob '!RecompiledFuncs.s*/**' --glob '!scratch_batch*/**' 'M_AUDTASK|audio.*(output|dest|dma)|image.*(stage|dest|dma)|dma.*(dest|len)|rs64.*(image|dma)|801496B0|801496F8|osAiSetNextBuffer|queue_samples' ../N64Recomp ../rogue_squadron64 src lib
```

Record the payload producer-to-consumer table and conclusion in
`scratch/agent/s2504_m5_pcm_payload_writer_audit/audit.md`.
