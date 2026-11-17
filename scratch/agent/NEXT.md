# NEXT (s7510)
HYPOTHESIS-ID: post-rsp-generator-next-class

Context: the RSP generator is audited end to end (FD s7507, FE s7508, FF s7509 + s7091/s7092/s7093; all H-equal). CURRENT-TRUTH
item 21 applies: take a NEW idiom-class audit (ITERATION.md item 3 model: enumerate the whole class, classify every site, guard or
prove dead, close) or the next open 3c rung. Do not write a backlog-exhausted block.

Work unit: class FG, chosen by a boring-first grep. Candidate (check PORTING-STATE first that it is not already closed:
`grep -n '^## Session' PORTING-STATE.md | grep -i 'dma\|s7094'`): RSP DMA address/length semantics vs ares
(librecomp rsp.hpp dma_rdram_to_dmem / dma_dmem_to_rdram + the s6713 fast path): hardware masks SP_MEM_ADDR to 8-byte alignment
(bits 3-11, bit 12 selects IMEM), DRAM_ADDR to 8-byte alignment and 24 bits, rounds length (bits 0-11)+1 up to 8, and wraps the
DMEM offset at 4 KB. If s7094 (rs64_s7094_dma_shape) already proved every live DMA is aligned/unwrapped, FG = an offline model
diff of our copy loops vs ares on all (mem,dram,len) shapes s7094 logged + synthetic misaligned/wrap cases, with mutation controls.
If it is already closed, pick the next unaudited class instead and name it here before building.
Hypotheses: H-equal (0 diffs on live + synthetic) / H-dead (diff only on shapes no live DMA uses) / H-live (a live shape differs ->
fix in lib/ + export.sh + commit, one L4 300 s hold).
Discriminating outcome: diff list split by live-shape use. No game run unless H-live.
