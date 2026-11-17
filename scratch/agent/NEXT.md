# NEXT (s7511)
HYPOTHESIS-ID: ai-dma-shape-vs-hardware

First: fold s7510_fg_levels from SOAK-RESULTS if it ran (score 0 -> FG CLOSED 6 levels in CURRENT-TRUTH item 20; score 1 -> read
the DIFF rows in scratch/s7510_fg_levels/out.txt, fix pi.cpp do_rom_read to the hardware rule, export.sh + commit).

Work unit: class FH, AI DMA shape vs hardware. Hardware (mupen64plus-core rs64-oracle src/device/rcp/ai/ai_controller.c, n64brew AI):
AI_DRAM_ADDR & 0xFFFFF8 (8-byte aligned, 24-bit), AI_LEN & 0x3FFF8 (18 bits, multiple of 8), a write with len 0 queues nothing.
Ours: librecomp ai.cpp osAiSetNextBuffer_recomp -> ultramodern::queue_audio_buffer(rdram, r4, r5) with no masking.
Check the boring thing first: read mupen's ai_controller.c write path and ultramodern queue_audio_buffer; then census the live
(addr, len) pairs. rs64_log_ai_output / rs64_log_ai_status already log set-next addr+len (find their env gate in src/).
Hypotheses: H-canon (every live pair has addr&7=0, len&7=0, len<0x40000 -> identical) / H-dead (non-canonical only in boot/silence)
/ H-live (a live pair differs, e.g. len not a multiple of 8 -> we play extra/fewer samples: fix to the hardware mask, one A/B).
Measurement: one run, 2 arms (L4 dd1, L15 dd8 21:9) via tools/g1e_owner_quiet_arms.zsh (see s7510 entry for the exact command,
mkdir R first), offline classifier tools/s7511_ai_dma_shape.py with synthetic + mutant controls. Outcome = per-class live counts.
