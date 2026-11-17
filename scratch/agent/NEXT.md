# NEXT (s7512)
HYPOTHESIS-ID: vi-register-shape-vs-hardware

First: fold s7511_fh_levels from SOAK-RESULTS if it ran (score 0 -> FH CLOSED 6 levels in CURRENT-TRUTH item 20; score 1 -> read
the DIFF rows in scratch/s7511_fh_levels/out.txt, and if a live non-canonical AI buffer exists, fix osAiSetNextBuffer_recomp to the
hardware rule (len & 0x3FFF8, addr & 0xFFFFF8, libultra hdwrBugFlag + AI delayed carry), export.sh + commit).
The recipe sits in soak_queue/ (moved there from hold/ at the end of s7511).

Work unit: class FI, VI register shape vs hardware. The game reaches the VI only through the libultra wrappers librecomp
replaces (src/main/upstream_compat.cpp osViSwapBuffer_recomp / osViBlack_recomp; lib/N64ModernRuntime/librecomp/src/vi.cpp
osViSetMode / SetSpecialFeatures / SetXScale / SetYScale). Check the boring thing first: the s7511 grep showed 0 `lui 0xA4xx`
in the recompiled game code, so no raw VI register writes; re-check for 0xA440 specifically.
Hardware: VI_ORIGIN & 0xFFFFFF, VI_WIDTH & 0xFFF, VI_X_SCALE/Y_SCALE 12-bit fixed 2.10 (+ offset field), VI_CONTROL type/AA/gamma
bits; libultra osViSwapBuffer stores the framebuffer vaddr and __osViSwapContext writes osVirtualToPhysical(fb) (+ the mode's
origin offset). Reference: mupen64plus-core src/device/rcp/vi/vi_controller.c in the rs64-oracle checkout, n64brew VI page.
Ours: what values RT64 receives (ultramodern VI state -> RT64 VI regs) per swap/mode change.
Hypotheses: H-canon (every live origin/width/scale already in hardware range -> masks are no-ops) / H-dead (out-of-range only at
boot/black frames) / H-live (a live field exceeds its hardware width, e.g. origin above 16 MB or width > 0xFFF at dd8 21:9 wide
fb, and RT64 uses the unmasked value -> hardware would wrap: decide which is right, fix or prove intended).
Measurement: one census log (one env flag, existing [phase]/swap logs if they carry the fields, else a new ROGUESQ_LOG_VI_SHAPE line),
2 arms (L4 dd1, L15 dd8 21:9) via tools/g1e_owner_quiet_arms.zsh (same command shape as s7511, R=scratch/s7512, mkdir R first),
offline classifier tools/s7512_vi_shape.py with synthetic + mutant controls. Outcome = per-field live in-range / out-of-range counts.
Note: the wide-fb opt-ins (ROGUESQ_ASPECT, FB_WIDTH > 796) deliberately go past retail widths; classify them separately from
retail-shaped values, they are not defects unless they exceed the hardware register width.
