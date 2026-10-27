# NEXT: G3c(b) spike pinned-Y: fold s6369 DMA-window soak
HYPOTHESIS-ID: g3c-owner-visual-b
Soak s6369_spike_dmawin (queued) logs `[spike-dma] ... covering=C/N` after each `[spike-dmem]` row.
Hypotheses: H-stale-slot (C=0, N>0: nothing DMA-loads 0x43A/0x462 -> ucode-written/stale constant; ask owner about ROGUESQ_CULL_SPIKE default-on), H-loaded (C>0: trace dram source to its writer, ask if value legit), H-ring-miss (N=0: DMA path not hooked; fix before concluding).
Fold: grep '\[spike-dma\]' in scratch/agent/m6/g1_lvl2s6369spikedmem/run.log, tabulate C/N vs pinY-resident rows (117/120 earlier).
