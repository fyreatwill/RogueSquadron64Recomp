# NEXT: owner reports first; otherwise runtime RSP DMA + cop0 model vs hardware SP DMA
HYPOTHESIS-ID: rsp-dma-cop0-model
Context: the recompiled-RSP layer is audited end to end at the instruction level (s7091 fixups, s7092 VU memory +
divide, s7093 scalar lowering, all tools exit 0). What is left is the RUNTIME model the generated code calls:
lib/N64ModernRuntime/librecomp/include/librecomp/rsp.hpp dma_rdram_to_dmem (line ~225) / dma_dmem_to_rdram (~346), the
SET_DMA_MEM / SET_DMA_DRAM / DO_DMA_READ / DO_DMA_WRITE macros, and the cop0 reads RSPRecomp hard-codes (SP_STATUS,
SP_DMA_FULL, SP_DMA_BUSY, SP_SEMAPHORE all read 0; SP_STATUS / SEMAPHORE writes ignored).
Hypotheses: H-dma-ok (every DMA the 3 TUs issue lands the same bytes as hardware) vs H-dma-shape (a field the runtime
ignores is used: RD_LEN count (bits 12-19) / skip (bits 20-31) for multi-row DMAs, length rounding to 8 bytes,
dram_addr &0xFFFFF8 vs hardware 0xFFFFF8, mem_addr &0xFF8 + bit 12 IMEM select, DMEM wrap at 0x1000 within one
transfer) vs H-cop0 (ucode branches on a status/semaphore/DMA_FULL value hardware would return differently, e.g.
SP_STATUS signal bits used as a yield/flag channel).
Unit (offline, one tool tools/s7094_dma_census.py + a host test):
1. Census every mtc0 SP_RD_LEN / SP_WR_LEN site in the 3 compiled TUs (s7093's parser + ROM decoder:
   `import s7093_su_census`): the source register's reaching value where it is a constant, and whether count/skip bits
   can be non-zero. Also every mfc0 site: which branch consumes the value, and what hardware would return there.
2. Host test: dma_rdram_to_dmem / dma_dmem_to_rdram (extracted from the live rsp.hpp like s7092 run.sh does) vs a
   byte-level reference written from cxd4 (../rs64-oracle/src/mupen64plus-rsp-cxd4 SP DMA path in module.c / su.c) and
   n64brew SP DMA rules, over random (mem, dram, len, count, skip) incl. wrap at DMEM 0xFF8 and unaligned inputs.
Controls: positive = mutate the reference length rounding (len+1 not rounded to 8) and show the test flags it; count
control = mtc0 RD_LEN/WR_LEN site totals equal s7093's C-section counts (SP_RD_LEN=6, SP_WR_LEN=2).
Expected outcomes: 0 diffs on every shape the ucode uses (closes the RSP runtime layer), or a named field / site ->
fix in rsp.hpp (lib/: then ./submodule-patches/export.sh + commit), L6 boot to flight (`zsh scratch/s7089/run.zsh`).
