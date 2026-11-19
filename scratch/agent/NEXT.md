# NEXT (s7645)
HYPOTHESIS-ID: owner-items-wait

G6a (rumble), G6b (F6 controls), G6c (stand-ins) and the G5 looks wait only on the owner (docs/OWNER-OPT-INS.md). If the owner
reports on any of them, take that first. Do NOT schedule a ladder-item-4 REVISIT or the rename sweep.

Work unit if no owner report: class TS-4 = gfx LLE task vs guest PI DMA / CPU on the RDRAM a gfx task reads (display list,
vertices, textures, matrices). TS-3 (s7644, CURRENT-TRUTH item 31) closed the audio side: only the over-declared ucode_data tail
overlaps, retail-identical. Hypotheses for gfx: H-clean (no PI DMA lands in a range a running gfx task reads: the game
double-buffers), H-live (an overlay/asset PI chunk lands in a DL/texture the RSP/RDP is still reading = port timing hardware would
not allow; candidate source of single-frame drops), H-retail (same overlap exists by design, e.g. streamed terrain textures).
Instrument: extend src/rsp/s7644_rspdma.cpp with a gfx mode (ROGUESQ_S7644_RSPDMA=2): per gfx task record the RDRAM ranges the
F5 ucode DMAs from (hook rs64 LLE gfx DMA reads in main.cpp/dpc path) with task start/end, and per PI DMA classify overlaps by
state copy/run/idle and changed bytes, as in TS-3. Control: RSPDMA_CTL=1 synthetic line. Arms: L1 + L4 dd2 FPS60 16:9 120 s via
`env R=$PWD/scratch/s7645/run HOLD=120 ALLOW_SLOW=1 ARMS="2:g1:ROGUESQ_S7644_RSPDMA=2+ROGUESQ_S7644_RSPDMA_CTL=1 2:g4:ROGUESQ_FORCE_SAVE_MISSION=4+ROGUESQ_S7644_RSPDMA=2+ROGUESQ_S7644_RSPDMA_CTL=1" zsh tools/g1e_owner_quiet_arms.zsh`.
Outcomes: run-state overlaps with chg>0 = H-live (name the DMA rom_off + guest pc and the task's DL); 0 with ctl firing = H-clean.
Rules: never launch under lldb; never touch build/saves; one game at a time; SIGKILL only.
