# NEXT (s7403)
HYPOTHESIS-ID: replaced-libultra-boot-globals

s7402 closed class BL (side-effect contract): osClockRate fixed (ROGUESQ_S7402_CLOCKFIX default on), sim-latent.
Fold first: soak s7402_clock_levels (L5/L10/L15, pass = alive, 0 crash, 1 boot row applied=1 now=46875000, all clk rows 46875000).

Work unit, class BM (boot-global contract: what IPL3 + retail osInitialize leave in low memory / libultra data that the port's
bootstrap may not):
1. Enumerate every live guest READ (tools/s7402_side_effects.py scan(), kind R/A, live() filter) of 0x80000300-0x8000033F
   (osTvType 300, osRomType 304, osRomBase 308, osResetType 30C, osCicId 310, osVersion 314, osMemSize 318, osAppNMIBuffer 31C..)
   and of libultra data words 0x80039100-0x8003910F (osClockRate, osViClock) plus any other libultra .data word a live game
   function reads.
2. For each, the retail value (IPL3 for an NTSC 6102-class cart, osInitialize stores) vs the port's (grep recomp.cpp /
   librecomp bootstrap for the address; runtime witness = one boot log line dumping the words at the first game-thread entry).
3. Hypotheses: H-none (every live-read word matches retail), H-unset (port leaves 0 / ROM data where IPL3 writes),
   H-value (port writes a different value, e.g. osMemSize 8 MB vs expansion-pak logic, osResetType). Static first; runtime
   = ONE boot dump line, two arms only if a fix lands (default-on env, =0 old), with a planted control.
