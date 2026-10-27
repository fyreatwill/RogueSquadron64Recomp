# NEXT (RESUME): G3c(b) spike pinned-Y: fold s6369 DMA-window soak
HYPOTHESIS-ID: g3c-owner-visual-b
s6370 only committed the extended `[spike-dma]` line (cum_cov43A/cum_cov462/cum_ctl500/cum_events); it is NOT yet built. First: rebuild (DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build), confirm it compiles (counters must be defined in the lib/N64ModernRuntime patch; apply.sh state is current).
Then fold SOAK-RESULTS s6369_spike_dmawin: grep '\[spike-dma\]' in scratch/agent/m6/g1_lvl2s6369spikedmem/run.log.
Hypotheses: H-stale-slot (C=0, N>0: ucode-written/stale constant; ask owner about ROGUESQ_CULL_SPIKE default-on), H-loaded (C>0: trace dram source to writer, ask if value legit), H-ring-miss (N=0: DMA path not hooked; fix first).
