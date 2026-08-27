# Session 2505 — M5 RSP image destination to AI-table join

## Scope and discriminator

This was a static-only census of the active image-arm output path, the
generated AI-buffer producer/consumers, and the host DMA observer. The AI
table is `D_801496B0`, with sixteen entries derived as `root + i*0x300`.
The discriminator was a table keyed by the relevant guest PC, source field,
DMA direction, destination expression, length, and AI-buffer derivation.

## Producer-to-consumer table

| site | operation | source / destination | length | relation to `D_801496B0[i]` |
|---|---|---|---:|---|
| `0x8008ED70` | `rs_malloc` | returns the AI allocation; stored at `D_801496B0` | `0x3000` | dynamic AI root |
| `0x8008EDB8` | sixteen stores | `D_801496B0 + 4 + i*4 = root + i*0x300` | `0x300` each | AI entries |
| `0x8008EE00` | `osAiSetNextBuffer` | `D_801496B0[0]` | `0x300` | AI consumer |
| `0x8008EE84` | `osAiSetNextBuffer` | `D_801496B0[index]` | `0x300` | rotating AI consumer |
| RSP `L_12E0` / `L_13B0` | image stage 2 and DMA write | DMEM `0x6F0..0x98F` to `SP_DRAM_ADDR = MEM_W(0x44, r2)` | `0x300` | no AI-root expression |
| RSP `L_1314` / `L_13B0` | image stage 3 and DMA write | DMEM `0xCB0..0xE47` to `SP_DRAM_ADDR = MEM_W(0x348) + 0x100` | `0x198` | no AI-root expression |
| host `rs64_audio_image_stage` | observer | records stage `dest` and validates observed windows | `0x300`/`0x198` | observes only |
| host `rs64_probe_audio_dma_write` | observer | records each `DO_DMA_WRITE` `dram_addr`, length, and payload hash | variable | no static AI-root join |
| `queue_audio_buffer` → `queue_samples` | consumer | reads the guest pointer passed by `osAiSetNextBuffer` | `0x300` | consumes; does not populate |

The image-stage fixup is an observer around the generated RSP calls; it does
not alter the DMA destination. The RSP destination is read from task/image
state in DMEM at runtime. The generated AI table’s root is the return value of
`rs_malloc`, so its physical RDRAM address is not a compile-time constant.
Observed image windows are runtime observations, not proof that the allocator
can never return one of those addresses.

## Result

Selected: **`H-rsp-destination-unresolved`** at the static boundary.

The table proves that image DMA and AI-buffer setup have different source
expressions and that the host AI path is a consumer, but it cannot compare a
DMEM-loaded runtime destination with the allocator’s returned root. No
`D_801496B0[i]` equality was found, and no explicit inequality is provable
without a runtime allocator/destination join. No build, runtime behavior,
address remap, or mitigation changed.
