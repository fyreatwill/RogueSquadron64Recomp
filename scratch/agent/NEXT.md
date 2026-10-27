# NEXT: G3c(b) spike pinned-Y: fold s6371 [spike-cov] soak
HYPOTHESIS-ID: g3c-owner-visual-b
Soak s6371_spike_cov (queued, built s6371) logs each DMA covering DMEM 0x43A with its post-DMA value. Fold: grep '\[spike-cov\]' scratch/agent/m6/g1_lvl2s6371spikedmem/run.log; count PIN lines (v43A==F55C) and compare k with spike rows' cum_cov43A.
H-loaded (PIN present): trace dram source to writer, ask if legit. H-ucode-write (no PIN while spike rows show Y -681): ucode overwrites DMEM after load -> inspect which RSP code writes 0x43A. If neither resolves, ask owner about ROGUESQ_CULL_SPIKE default-on.
