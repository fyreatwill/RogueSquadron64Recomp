# NEXT: G1d step 16 - prove/refute heap starvation as cause of the NULL-dest DMA at wide mission start
HYPOTHESIS-ID: g1d-widescreen
Known (s6123): 21:9 crashes 5/5 right after a PI DMA with dram=0x00000000 (ROM 0x101A5E20, size 0x1000) = failed allocation. Queued control s6123_g1d_dmalog_ctl43 (4:3 + ROGUESQ_LOG_DMA) - read its SOAK-RESULTS line + scratch/agent/m6/g1_lvl1s6123_ctl43_dma/ first.
Hypotheses: H-heap (wide fbs starve heap -> NULL) ; H-stride (some table sized 512-based overflows); H-unrelated (the dram=0 DMA also exists in 4:3 and the real fault is elsewhere).
Discriminator: ctl has no dram=0 DMA => H-heap/H-stride live. Then add an alloc-failure log (requested size, heap top) and run 4:3 vs 21:9 arms in one iteration; also an arm with pfm width fixed at 640 for flip buffers only to see if the NULL moves.
Fix direction: place wide framebuffers in the extra mapped RAM above 0x80800000 if RDP/RT64 masking allows (<16 MB physical), not shrink heap. Name the writer (rule 11).
