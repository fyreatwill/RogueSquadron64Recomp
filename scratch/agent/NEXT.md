# NEXT: name the non-RT64-writeback writer of hangar colour-image column 511 (buffer 0x656400)
HYPOTHESIS-ID: hangar-renderer-artifacts

s4637 refuted RT64 colour writeback as writer (ROGUESQ_NO_WB_W=512; control zeroes 0x6AB400 body but 0x656400 col 511 stays noisy 2/2).
Remaining: H-cpu (recomp stores), H-rdp (host RDP path other than writeback), H-dma (SP/PI DMA).
Discriminator: arm a physical write-watch (recomp store path, src/main/upstream_compat.cpp) on 0x656400+1022+1024*r, r=0..239 plus positive control mid-row col 100; log PC/source once per frame in the same run as ROGUESQ_EDGE_DUMP and ROGUESQ_NO_WB_W=512. Check first whether rs64_m5_host_write_census already lists sources touching that range (cheap, existing).
Outcomes: CPU PC fires => read that function; nothing fires but dump noisy => RDP/DMA host-side path.
Tools: scratch/agent/s4637_wb.sh, s4637_an.py, s4636_edge.sh.
