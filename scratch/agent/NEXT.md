# NEXT (RESUME): G3c(b) spike pinned-Y: fold s6369 DMA-window soak
HYPOTHESIS-ID: g3c-owner-visual-b
s6369 fold: pure H-stale-slot refuted (7293 covering DMAs); ring sampled too sparsely. Next: log each covering DMA at occurrence (dram src,len,dmem,task) and compare dram bytes at 0x43A with pinned Y -681 (equal => H-loaded; differ => ucode overwrites). Also unbuilt s6370 fields: rebuild first.
Then fold SOAK-RESULTS s6369_spike_dmawin: grep '\[spike-dma\]' in scratch/agent/m6/g1_lvl2s6369spikedmem/run.log.
Hypotheses: H-stale-slot (C=0, N>0: ucode-written/stale constant; ask owner about ROGUESQ_CULL_SPIKE default-on), H-loaded (C>0: trace dram source to writer, ask if value legit), H-ring-miss (N=0: DMA path not hooked; fix first).
