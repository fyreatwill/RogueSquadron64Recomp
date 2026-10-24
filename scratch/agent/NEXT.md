# NEXT: G1c phase 2 - name the beginFrameDLChunk+12168 fault at dd3 (arena arm)
HYPOTHESIS-ID: g1c-phase2-drawdist
s6086 result: arena removes heap NULLs but L1 px4 dd3 SIGBUS 5/5 at beginFrameDLChunk+12168, si_addr=0x38000000{0,4} (same family as s6062 px3_dd2).
Hypotheses: H-DL (guest DL buffer / chunk cap overrun at dd3), H-arena-ptr (pool pointer >=0x80800000 reaching a guard/mask in this function), H-stride (64-wide bitmap). Discriminator: run arena arm px4 dd3 under lldb (or log regs at fault: disassemble beginFrameDLChunk+12168 in funcs_*.c, find the load, print base reg); then same run with BIGARENA=0 px2 dd3 (heap fits) - if it crashes identically, arena is exonerated (H-DL).
First fix: don't reset bump in rs64_s6086_arm (src/main/upstream_compat.cpp). Fold control s6086_ctl_px4_dd3_noarena from SOAK-RESULTS.
