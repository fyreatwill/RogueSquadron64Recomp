# Next work unit: resolve the DMEM 0xCC0..0xCD0 coverage gap

HYPOTHESIS-ID: m5-dmem-cc0-gap

S3698 qualified the per-byte coverage table. All 512 hangar source rows had
zero payloads; 255 rows had no observed DMEM writer for exactly `0xCC0..0xCD0`,
while the other observed bytes were zero-valued vector stores. Retail's named
writer families remain independent ground truth, but the fresh oracle process
did not emit its shutdown histogram.

Competing hypotheses:

- `H-UninstrumentedDMEMWriter`: a DMEM write path exists but bypasses the
  current `rs64_m5_audio_dmem_store` witness.
- `H-GenuineZeroGap`: no writer touches `0xCC0..0xCD0`; the zero bytes are
  preserved or initialized state.
- `H-RetailLayoutMismatch`: the port's source-DMA/DMEM layout differs from
  retail's image producer, so the apparent gap is not the retail field.

Discriminator: refresh retail ground truth with the whole-RDRAM watch and
hangar source-span watch, then in one build enumerate every port DMEM write
path that can touch `0xCC0..0xCD0` (scalar/vector store hooks and DMEM DMA
copies) and carry a per-byte writer record into each source-DMA row. A writer
record in the gap selects `H-UninstrumentedDMEMWriter`; no record in the gap
with positive controls selects `H-GenuineZeroGap`; a complete port record that
still cannot reconcile the retail writer contract selects
`H-RetailLayoutMismatch`.

Exact commands:

1. `tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/Cellar/mupen64plus/2.6.0/lib/mupen64plus/mupen64plus-video-rice.dylib --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --secs 65 --hit-cap 10000 --watch-write 0x0:0x800000 --watch-write 0x1797B0:0x179930 --pc-hist-watch 1 --pc-hist-phase 0x006AB400:512 --vi-trace`.
2. `rg -n "dmem\\[|dma_.*dmem|audio_dmem|RSP_MEM_ADDR|SP_WR_LEN" src lib/N64ModernRuntime lib/rt64` and add the complete gap witness in the existing regeneration-preserved path.
3. `cmake --build build --config Debug --target RogueSquadron64Recomp`, then
   run the qualified real-audio/LLE-solo/spin-yield/autopilot route with
   `ROGUESQ_LOG_M5_RSP_SOURCE=1` and `ROGUESQ_LOG_M5_SOURCE_WRITER=1`.

The run is invalid unless the RSP, DMEM, and 512-row source-DMA controls all
fire in the same process.
