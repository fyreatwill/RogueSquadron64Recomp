# NEXT: M4 matrix-span discriminator (v8..v15 source)
HYPOTHESIS-ID: m4-vge-store-boundary-ground-truth

RESUME: s4626 VMADH 4,128/4,128; s4628 store clean; s4629 VGE pure clamp;
s4630 vertex input (RDRAM 0x720320+, DMEM 0x280) equals retail at hangar for 13
sampled blocks (56 words, 0 diffs). Only the matrix operand survives.

Hypotheses:
- H-matrix-rdram: port RDRAM at 0x700000/40/80 (-> DMEM 0x590/0x5D0) differs
  from retail at hangar entry (writer of the matrix differs).
- H-matrix-compose: RDRAM matrix equal, the ucode step composing v8..v15 diverges.
- H-no-diff: the operand match means the divergence is later (clipping / RDP).

Discriminator: extend `rs64_m4_dma_probe` to print 16 words of RDRAM at the DMA
source for mem 0x590/0x5D0/0x610 reads (one build); compare against retail
`RS64_ORACLE_PEEK` of 0x700000..0x70003C at the FIRST hangar sample (retail value
changes later: first sample 0001ffff, later 0000ffff). Retail peek cap is 16
words per run (raising it needs `tools/oracle/build.sh` approval - ask or use
multiple runs; see scratch/agent/s4630_m4_operand_source/oracle_arm.sh).
Equal => H-matrix-compose (trace ucode ops before L_162C, DMEM 0x590..);
different => trace the RDRAM writer with the oracle write watch.
Run git from the repo root (cwd drifts); use absolute paths.
