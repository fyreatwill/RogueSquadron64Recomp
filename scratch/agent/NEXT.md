# NEXT: name the hot path of the gfx RSP task at 21:9 dd4 (G5e WIDEWIN cost, s7013)
HYPOTHESIS-ID: dd-wide-window
Context: s7013 refuted H-room: caps 4096/5120/5632 give fps 54.2/45.7/43.3, rsp 13.06/14.13/14.41 ms (~0.9 ms per 1000 cells). The gfx RSP task
(~13 ms/frame at the retail-size window) is the binding term; WIDEWIN can only be free if that task gets cheaper per cell.
Hypotheses (where the gfx task host time goes):
 H-vtx: vertex transform/lighting ucode loop dominates (cost ~ vertex count) -> optimise the recompiled vector ops in that block.
 H-clip: near/far clip + tri setup path dominates (cost ~ triangles crossing planes) -> look at the clip block / VRCP path.
 H-dma: DMA/DL fetch + dispatch overhead (rsp_dma, per-command dispatch) dominates -> batch DMA / cheaper dispatch.
 H-glue: host glue (dpc_bridge, spike cull, W clamp, RDP FIFO handoff) dominates -> cheaper bridge.
Discriminator (one run): env NOCAP=1 ASP=21:9 CULL=1 zsh scratch/s7013/arm.zsh 4 4 p1 "ROGUESQ_DD_MELT=1 ROGUESQ_DD_WIDEWIN=1 ROGUESQ_DD_WIDEWIN_CAP=8192"
 and, once in flight (>=140 s after launch), `sample RogueSquadron64Recomp 20 -file scratch/s7013/sample_p1.txt`, then
 python3 tools/sample_game_threads.py scratch/s7013/sample_p1.txt 12 and a per-function self-time tally of the SP Task / Gfx thread
 (top 20 leaf symbols, factor5_ucode block addresses). Positive control: the SP Task thread must show >= ~75% busy samples in flight (13/16.7 ms).
 Same run second sample with WIDEWIN off is not possible (no runtime toggle except tog), so use WIDEWIN=tog and take two 20 s samples, or accept
 one sample: the question is the shape, not the delta. Each outcome names the block to optimise; then build the optimisation and measure rsp ms.
Delete run.log after grepping.
