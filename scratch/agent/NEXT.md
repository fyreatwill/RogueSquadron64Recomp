# NEXT work unit (s2506) — runtime-join RSP image destinations to AI entries

HYPOTHESIS-ID: m5-pcm-payload-writer-provenance

## Single work unit

Build one phase-gated runtime join that records every image-arm
`DO_DMA_WRITE` destination/length and the allocator-derived
`D_801496B0[i] = root + i*0x300` entries in the same target phase. Include a
positive control proving both the image-DMA observer and AI consumer observer
fire in that run. Do not use the superseded `0x801096B0` address. Do not alter
audio behavior or remap any destination.

## Competing hypotheses and discriminator

- `H-rsp-destination-joined`: a same-run destination equals a recorded
  allocator-derived AI entry with compatible length.
- `H-rsp-destination-distinct`: all same-run image destinations are unequal to
  every recorded AI entry, with both positive controls passing.
- `H-rsp-destination-unresolved`: either observer/control is absent or the
  runtime records do not preserve enough identity to decide.

The discriminator is one same-run table keyed by phase, audio ordinal/image
ordinal, DMA destination/length, allocator root, entry index, and derived
entry. Equality selects `H-rsp-destination-joined`; complete inequality with
positive controls selects `H-rsp-destination-distinct`; otherwise select
`H-rsp-destination-unresolved`.

## Exact commands

```sh
rg -n -i --glob '*.c' --glob '*.cpp' --glob '*.h' --glob '*.py' --glob '*.toml' --glob '!RecompiledFuncs.s*/**' --glob '!scratch_batch*/**' 'M_AUDTASK|audio.*(output|dest|dma)|image.*(stage|dest|dma)|dma.*(dest|len)|rs64.*(image|dma)|801496B0|801496F8|osAiSetNextBuffer|queue_samples' ../N64Recomp ../rogue_squadron64 src lib
```

Record the complete runtime table and conclusion in
`scratch/agent/s2506_m5_rsp_destination_runtime_join/audit.md`.
