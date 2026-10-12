# NEXT: name the writer of hangar colour-image column 511 (buffer 0x656400)
HYPOTHESIS-ID: hangar-renderer-artifacts

RESUME: s4636 found column 511 of the 512-wide colour image at 0x00656400 is per-frame noise (buffer 0x006AB400 col 511 is zero). Writer candidates:
 H-rt64-wb: RT64 writes framebuffer back to RDRAM and spills one pixel past width.
 H-cpu: recompiled game code (span/copy loop with width or stride error).
 H-rdp: RDP primitives (rect/fill/scissor) from the display list reaching x=511.
Discriminator (offline first): grep lib/rt64 for RDRAM writes (FB readback); if none, add a write-watch in the recomp store path (hooks in src/main/upstream_compat.cpp) for physical 0x656400+1022+1024*r (r=0..239), log PC once per frame, same run as ROGUESQ_EDGE_DUMP. Positive control: watch a mid-row address (col 100) that must fire.
Outcomes: fires with CPU PC => H-cpu (read that function); no fire but dump noisy => RT64 / RSP / RDP DMA; then instrument RT64 writes.
Tools: scratch/agent/s4636_edge.sh (4 runs), s4636_an.py, s4636_an2.py.
