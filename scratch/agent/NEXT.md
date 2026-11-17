# NEXT (s7513)
HYPOTHESIS-ID: si-cont-shape-vs-hardware

First: fold s7512_fi_levels from SOAK-RESULTS if it ran (score 0 -> FI CLOSED 6 levels in CURRENT-TRUTH item 20; score 1 -> read the
diff rows in scratch/s7512_fi_levels/out.txt; a live diff with ROGUESQ_VI_BLACK_RETAIL on is a real regression -> fix or flip the default).

Work unit: class FJ, SI / controller (joybus) data shape vs hardware. The game reaches the SI only through libultra wrappers librecomp
replaces (lib/N64ModernRuntime/librecomp/src/cont.cpp: osContInit / Reset / StartReadData / GetReadData / StartQuery / GetQuery /
SetCh, motor; EEPROM/Pfs in librecomp too). Boring check first: which wrappers have callers in
/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs (s7512 grep pattern: `<name>_recomp(rdram, ctx)`), and whether any
retail __osSiRawStartDma / __osContRamRead path is still recompiled from the ROM (syms 0x8002AC30 osContStartReadData etc.).
Hardware/libultra: OSContPad {u16 button, s8 stick_x, s8 stick_y, u8 errno}, OSContStatus {u16 type, u8 status, u8 errno}; retail
osContGetReadData copies from the PIF block with CONT_NO_RESPONSE_ERROR when absent; button mask 0xFFFF but bits 0x0030 (reserved) and
the stick range +-127 (real pads ~+-80). Reference: retail ROM disassembly (mips64-elf-objdump, ROM off = vram-0x80000440+0x1040),
mupen64plus-core src/device/controllers in lib/rt64/src/contrib/mupen64plus-core or the rs64-oracle checkout.
Hypotheses: H-canon (every OSContPad/Status written to guest RAM is a shape a real pad + PIF can produce) / H-dead (odd shapes only with no
pad, at boot) / H-live (a live write differs: e.g. errno for ports 2-4, status bits, type 0x0005 vs pak, stick beyond the s8 clamp,
reserved buttons set) -> fix to the hardware rule.
Measurement: one census env (ROGUESQ_LOG_CONT_SHAPE=1, every guest write from the cont wrappers: n, t, wrapper, port, raw bytes), 2 arms
(L4 dd1, L15 dd8 21:9) via tools/g1e_owner_quiet_arms.zsh (command shape as s7512, R=scratch/s7513), offline tools/s7513_cont_shape.py
with synthetic + mutant controls and an in-run positive control (e.g. ROGUESQ_CONT_SHAPE_CTL=<n> writes one out-of-range stick into the
census record only).
