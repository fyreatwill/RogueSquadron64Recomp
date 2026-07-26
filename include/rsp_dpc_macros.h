#ifndef RSP_DPC_MACROS_H
#define RSP_DPC_MACROS_H

// Force-included into RecompiledFuncs (C) AND factor5_ucode (C++) targets.
// Header is split: C-safe MEM_WU at top, C++-only RSP DPC macros below.

// MEM_WU — unsigned-word RDRAM access. Upstream recomp.h defines MEM_W
// (signed int32) and MEM_HU/MEM_BU (unsigned half/byte) but no unsigned
// word variant. Recompile output occasionally needs it (e.g. funcs_7
// pointer comparisons). Mirrors MEM_W layout but loads as uint32_t.
#ifndef MEM_WU
#define MEM_WU(offset, reg) \
    (*(uint32_t*)(rdram + ((((reg) + (offset))) - 0xFFFFFFFF80000000)))
#endif

#ifdef __cplusplus

// RSP-side DPC MMIO macros emitted by RSPRecomp when the RSP ucode does
// `mtc0 reg, DPC_*` / `mfc0 reg, DPC_*` to access RDP control registers.
// Upstream librecomp does not provide these; our DPC bridge in
// src/rsp/dpc_bridge.cpp owns the relevant state. This header bridges
// them so the recompiled Factor5 ucode (factor5_ucode_recompiled.c)
// links cleanly without runtime-side modifications.

#include <cstdint>

extern uint32_t g_rsp_dpc_start;
extern uint32_t g_rsp_dpc_end;
extern uint32_t g_rsp_dpc_current;
// Bridge entry point — defined in src/rsp/dpc_bridge.cpp. Forwards the
// DPC byte range to RT64 for raw-RDP rasterization.
void rsp_dpc_submit(uint8_t* rdram, uint32_t start, uint32_t end);
// CURRENT read with bounded-poll escape — defined in dpc_bridge.cpp.
uint32_t rs64_dpc_current_read();

// Hardware semantics: writing DPC_START loads DPC_CURRENT with the same
// address; the RDP then consumes from CURRENT toward END. Our "RDP" (RT64)
// consumes instantly, so CURRENT snaps to END on every END write. Without
// the START->CURRENT reset, the ucode's ring-buffer wait loop (L_116C)
// spins forever when the previous task's END lands inside the new write
// window — that was the LLE-mode Gfx Thread wedge.
#define RSP_DPC_START(value)   do { uint32_t _v = (uint32_t)(value); g_rsp_dpc_start = _v; g_rsp_dpc_current = _v; } while (0)
#define RSP_DPC_END(value)     do { uint32_t _v = (uint32_t)(value); g_rsp_dpc_end = _v; g_rsp_dpc_current = _v; rsp_dpc_submit(rdram, g_rsp_dpc_start, _v); } while (0)
#define RSP_DPC_END_READ()     (g_rsp_dpc_end)
#define RSP_DPC_CURRENT_READ() (rs64_dpc_current_read())
#define RSP_DPC_STATUS_WRITE(value) do { (void)(value); } while (0)
#define RSP_DPC_STATUS_READ()  (0u)
#define RSP_DPC_CLOCK_READ()   (0u)
#define RSP_DPC_BUFBUSY_READ() (0u)
#define RSP_DPC_PIPEBUSY_READ() (0u)
#define RSP_DPC_TMEM_READ()    (0u)

#endif // __cplusplus
#endif // RSP_DPC_MACROS_H
