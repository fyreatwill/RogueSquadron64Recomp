# Next work unit: M5 Step 9g — why are all audio ucode DMA writes zero after early phase 4?

HYPOTHESIS-ID: m5-audio-destub-sequence

s4208: ucode writes DMEM->RDRAM into +0x7C buffers but all bytes zero from early phase 4 on (cum_nzbytes frozen 264405; phase-3 control nonzero). Live-tree patches only (tools/apply_s4208_dma_ring.py); never regen.

Hypotheses:
- H-src-dma-zero: DMEM->input DMA reads (source samples/ADPCM) arrive zero in DMEM (host DMA read path / address translation wrong).
- H-state-zero: inputs fine, but loop/ADPCM state or volume ramps in DMEM are zero so mix is zero.
- H-cmd-skip: ucode command dispatch skips the mix commands (cmdlist ops differ from phase 3).

Discriminator: extend ring to RDRAM->DMEM reads (dram, len, nz of RDRAM source and of DMEM after) plus per-task DMEM nz hash at exit; compare phase 3 vs 5 in one run.
Outcomes: reads nz>0 in phase 5 but DMEM region zero => translation bug; reads zero => upstream source bytes at read address zero (address mismatch with +0x2C); reads nz and DMEM nz but writes zero => H-state/H-cmd, then count executed command ops.
