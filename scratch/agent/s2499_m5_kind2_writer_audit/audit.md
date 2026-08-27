# s2499 — kind=2 PCM-ring writer provenance audit

## Scope

This is a static census of the workspace sources. No build or runtime behavior
was changed. The target is the `kind=2` path in `src/main/main.cpp` and the
producer of `g_rs64_pcm_last_dma_phys`, with `queue_samples` as the first host
consumer boundary.

## Caller/producer table

| Symbol / boundary | Caller or producer | Inputs and effect | Interpretation |
|---|---|---|---|
| `rs64_pcm_writer_note` | `rs64_m5_pcm_writer_store` (`src/main/main.cpp:481`) | Converts a guest store address to physical form, records `kind=1`, preserves guest `pc` and value | Intended CPU/guest-store observation; no caller is present in this workspace outside the exported symbol itself |
| `rs64_pcm_writer_note` | `rs64_m5_pcm_writer_dma` (`src/main/main.cpp:488`) | Sets `g_rs64_pcm_last_dma_phys = addr & 0x007FFFFF`, saves length, then records `kind=2`, `pc=0`, `value=0` | DMA bookkeeping observation; not a guest CPU writer attribution |
| `rs64_m5_pcm_writer_dma` | `rs64_probe_audio_dma_write` (`lib/N64ModernRuntime/librecomp/src/rsp.cpp:961-962`) | Called after an image-stage RDRAM DMA range is hashed and appended to the active audio probe; passes `dram_addr`, `len`, payload FNV, and nonzero-byte count | The sole `kind=2` producer is the generated audio/image RSP DMA callback |
| `rs64_audio_join_pcm("source", ...)` | `ultramodern::queue_audio_buffer` (`lib/N64ModernRuntime/ultramodern/src/audio.cpp:78-85`) | Reads the writer snapshot for the supplied AI buffer pointer, then records the PCM source row | First downstream join point; it does not receive image-DMA identity |
| `queue_samples` | `ultramodern::queue_audio_buffer` (`audio.cpp:93`), host callback `main.cpp:3111` | Passes the same AI buffer pointer and sample count to the host callback; host queues bytes to SDL | First actual host PCM consumer; it is downstream of the independent AI ring/table pointer |

## Important negative census

`rg` found exactly one workspace call to `rs64_m5_pcm_writer_dma`, in
`rs64_probe_audio_dma_write`, and no workspace call to
`rs64_m5_pcm_writer_store`. The generated `RecompiledFuncs` tree described by
the project instructions is not checked out under this workspace, so this
result does not claim that external generated callsites do not exist. It does
establish that the runtime's `kind=2` path has no second producer or guest-PC
attribution in the sources available here.

The callback is part of the image-stage DMA observer: it is reached after
`probe->ranges` has recorded the DMA's destination, length, DMEM address,
output/yield/data overlap flags, event, payload hash, and nonzero count. The
`kind=2` wrapper then throws away the hash and nonzero count for the writer
state and supplies zero for `pc` and `value`. Its candidate/ring overlap can
prove that an image DMA touched a range, but cannot prove that a CPU store
created the PCM-ring contents or that the DMA is the source of a later AI
buffer.

## Discriminator result

This selects `H-kind2-host` at the requested writer-provenance boundary: the
`kind=2` row is host-side bookkeeping for an image/RSP DMA, not a game-side
PCM-ring writer. `H-kind2-generated` is refuted for the meaning “legitimate
generated CPU/image writer joined to a nonzero PCM consumer,” because no
consumer identity or stable producer-to-AI-ring relation enters this path.
`H-kind2-unresolved` remains applicable only to the still-open downstream
DMA-to-AI-buffer relation, not to the immediate `kind=2` producer itself.

No remap, guard, mitigation, or instrumentation change is authorized by this
audit. The next useful boundary is the external/generated CPU-store callsite
census for `rs64_m5_pcm_writer_store` and the actual writer of the AI ring
rooted at `0x801096B0`.
