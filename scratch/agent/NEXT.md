# NEXT (s7329): dd6 21:9 spill blocks — RSP-read? + byte-comparer negative control
HYPOTHESIS-ID: spill-rcp-dma-width
Context (s7328): the s7327 25-bit RSP DMA fix is visible (posed L1 dd8 16:9 with ROGUESQ_SPILL_FORCE=min:0x200000: old mask = rainbow
garbage near terrain, 37.8% px; fix = pixel-identical to no spill). Remaining: dd6 21:9 hangar route spills 2x 0x19DF70 per mission load.
Hypotheses: H-rsp-read (the 0x19DF70 blocks are DMA'd by the gfx/audio ucode -> were wrong before s7327, fixed now) vs H-cpu-only
(only the CPU touches them; s7327 irrelevant at dd6).
Measurement (offline-cheap first): which allocator owns 0x19DF70 (grep heaplog/ALLOCMAP in scratch/s7326/s7327_dd6_219/run.log).
Then ONE run: forced route L1 dd6 21:9 + ROGUESQ_SPILL_FORCE=19DF70 (check "[s7328] big req" lines for the L1 size first; use the
logged size) + ROGUESQ_S7324_RCPREF=ctl + ROGUESQ_S7317_ALLOCMAP=1 + ROGUESQ_RSP_DMA25_CTL=1, report tools/s7324_rcp_report.py:
direct_spill>0 in the forced block selects H-rsp-read; 0 with ctl PASS selects H-cpu-only. Pose arms (scratch/s7328/run.zsh, ARMS=)
DMA25=1/0 only if H-rsp-read.
Byte-comparer negative control: in rsp.hpp DMA25_CTL, also compare a spill read against itself (must be 0 differ) — or log one
non-spill read through both masks (identical by construction).
Parallel open (item 22): 46 audio reads of song-channel arrays freed 0-14 ms earlier at the scene transition.
