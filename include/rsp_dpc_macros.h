#ifndef RSP_DPC_MACROS_H
#define RSP_DPC_MACROS_H

// Force-included into RecompiledFuncs (C) AND factor5_ucode (C++) targets.
// Header is split: C-safe MEM_WU at top, C++-only RSP DPC macros below.

// MEM_WU — unsigned-word RDRAM access. Upstream recomp.h defines MEM_W
// (signed int32) and MEM_HU/MEM_BU (unsigned half/byte) but no unsigned
// word variant. Recompile output occasionally needs it (e.g. funcs_7
// pointer comparisons). Mirrors MEM_W layout but loads as uint32_t.
// s7576: total trunc.w.s / trunc.w.d for RecompiledFuncs (tools/apply_s7576_trunc_total.py). recomp.h's TRUNC_W_S/D are bare
// (int32_t) casts: UB for NaN / out-of-range, and clang -O2 provably deletes code on that basis (tools/s7576_trunc_census.py
// control). Measured s7576: no such deletion in the 1199 generated sites; these give the same arm64 fcvtzs result (saturate,
// NaN -> 0) with no UB. R4300 traps (Unimplemented) on an unrepresentable trunc, so every out-of-range value is a port-only
// event: it is reported (rate-limited) by rs64_s7576_trunc_oor. ROGUESQ_S7576_TRUNC_CTL=N reports the first N conversions
// as forced (positive control). C-safe.
#include <stdint.h>
#if defined(__aarch64__)
#include <arm_neon.h>
#endif
#ifdef __cplusplus
extern "C" {
#endif
extern int rs64_s7576_trunc_ctl;
void rs64_s7576_trunc_oor(uint32_t pc, double v, int is_d);
#ifdef __cplusplus
}
#endif
static inline int32_t rs64_trunc_w_s(float v, uint32_t pc) {
    if (__builtin_expect(!(v >= -2147483648.0f && v < 2147483648.0f) || rs64_s7576_trunc_ctl > 0, 0)) {
        rs64_s7576_trunc_oor(pc, (double)v, 0);
        if (!(v >= -2147483648.0f && v < 2147483648.0f)) return v != v ? 0 : (v < 0 ? INT32_MIN : INT32_MAX);
    }
#if defined(__aarch64__)
    return vcvts_s32_f32(v);
#else
    return (int32_t)v;
#endif
}
static inline int32_t rs64_trunc_w_d(double v, uint32_t pc) {
    if (__builtin_expect(!(v > -2147483649.0 && v < 2147483648.0) || rs64_s7576_trunc_ctl > 0, 0)) {
        rs64_s7576_trunc_oor(pc, v, 1);
        if (!(v > -2147483649.0 && v < 2147483648.0)) return v != v ? 0 : (v < 0 ? INT32_MIN : INT32_MAX);
    }
    return (int32_t)v; /* in range here: defined */
}
#define RS64_TRUNC_W_S(v, pc) rs64_trunc_w_s((v), (pc))
#define RS64_TRUNC_W_D(v, pc) rs64_trunc_w_d((v), (pc))

// s7575: total 32-bit div/divu for RecompiledFuncs (tools/apply_s7575_div_total.py). The generated C divide sits
// before the compiler's zero check; at -O2 its UB let clang delete 36 do_break checks. R4300 results on b == 0.
// Uses the enclosing function's `lo`/`hi` locals. C-safe.
#define RS64_DIV32(a, b) do { int32_t rs64_da_ = (int32_t)(a), rs64_db_ = (int32_t)(b); \
    if (__builtin_expect(rs64_db_ == 0, 0)) { lo = (uint64_t)(int64_t)(rs64_da_ < 0 ? 1 : -1); hi = (uint64_t)(int64_t)rs64_da_; } \
    else { lo = (uint64_t)(int64_t)(int32_t)((int64_t)rs64_da_ / rs64_db_); hi = (uint64_t)(int64_t)(int32_t)((int64_t)rs64_da_ % rs64_db_); } } while (0)
#define RS64_DIVU32(a, b) do { uint32_t rs64_da_ = (uint32_t)(a), rs64_db_ = (uint32_t)(b); \
    if (__builtin_expect(rs64_db_ == 0, 0)) { lo = (uint64_t)(int64_t)(int32_t)0xFFFFFFFFu; hi = (uint64_t)(int64_t)(int32_t)rs64_da_; } \
    else { lo = (uint64_t)(int64_t)(int32_t)(rs64_da_ / rs64_db_); hi = (uint64_t)(int64_t)(int32_t)(rs64_da_ % rs64_db_); } } while (0)

#ifndef MEM_WU
#define MEM_WU(offset, reg) \
    (*(uint32_t*)(rdram + ((((reg) + (offset))) - 0xFFFFFFFF80000000)))
#endif

#ifndef __cplusplus
// s7432 class CO: every fprintf in the generated C goes through rs64_diag_fprintf (src/main/main.cpp): ROGUESQ_DIAG_QUIET=1
// drops diagnostic stderr lines at source, ROGUESQ_DIAG_STAT=1 / *_TOGGLE measure their cost. stdio.h first so the macro
// cannot rewrite its declaration (later #include <stdio.h> is guarded).
#include <stdio.h>
int rs64_diag_fprintf(FILE* f, const char* fmt, ...);
#define fprintf(...) rs64_diag_fprintf(__VA_ARGS__)
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
// s7095: ROGUESQ_S7095_DPC=1 shadows every access against a hardware DPC model (src/rsp/s7095_dpc_model.cpp).
extern "C" int rs64_s7095_on;
extern "C" void rs64_s7095_start(uint32_t v);
extern "C" void rs64_s7095_end(uint32_t v);
extern "C" void rs64_s7095_status_write(uint32_t v);
extern "C" void rs64_s7095_end_read(uint32_t ours);
extern "C" void rs64_s7095_status_read();
// s7096: ROGUESQ_S7096_FWD=1 compares the hardware-consumed DPC byte stream with what the bridge forwards (src/rsp/s7096_fwd_cover.cpp).
extern "C" int rs64_s7096_on;
extern "C" void rs64_s7096_start(uint32_t v);
extern "C" void rs64_s7096_end(uint32_t v, const uint8_t* rdram);
// s7523: ROGUESQ_S7523_SLOWRDP=<rate>[,<gap>] serves every DPC read from a finite-rate RDP model (src/rsp/s7523_slow_rdp.cpp).
extern "C" int rs64_s7523_on;
extern "C" void rs64_s7523_start(uint32_t v);
extern "C" void rs64_s7523_pre_submit();
extern "C" void rs64_s7523_end(uint32_t v, const uint8_t* rdram);
extern "C" uint32_t rs64_s7523_end_read();
extern "C" uint32_t rs64_s7523_status_read();
static inline uint32_t rs64_dpc_end_read_hook() { if (__builtin_expect(rs64_s7523_on, 0)) return rs64_s7523_end_read(); if (rs64_s7095_on) rs64_s7095_end_read(g_rsp_dpc_end); return g_rsp_dpc_end; }
static inline uint32_t rs64_dpc_status_read_hook() { if (__builtin_expect(rs64_s7523_on, 0)) return rs64_s7523_status_read(); if (rs64_s7095_on) rs64_s7095_status_read(); return 0u; }
#define RSP_DPC_START(value)   do { uint32_t _v = (uint32_t)(value); if (rs64_s7095_on) rs64_s7095_start(_v); if (rs64_s7096_on) rs64_s7096_start(_v); if (rs64_s7523_on) rs64_s7523_start(_v); g_rsp_dpc_start = _v; g_rsp_dpc_current = _v; } while (0)
#define RSP_DPC_END(value)     do { uint32_t _v = (uint32_t)(value); if (rs64_s7095_on) rs64_s7095_end(_v); if (rs64_s7096_on) rs64_s7096_end(_v, rdram); g_rsp_dpc_end = _v; g_rsp_dpc_current = _v; if (rs64_s7523_on) rs64_s7523_pre_submit(); rsp_dpc_submit(rdram, g_rsp_dpc_start, _v); if (rs64_s7523_on) rs64_s7523_end(_v, rdram); } while (0)
#define RSP_DPC_END_READ()     (rs64_dpc_end_read_hook())
#define RSP_DPC_CURRENT_READ() (rs64_dpc_current_read())
#define RSP_DPC_STATUS_WRITE(value) do { uint32_t _v = (uint32_t)(value); if (rs64_s7095_on) rs64_s7095_status_write(_v); (void)_v; } while (0)
#define RSP_DPC_STATUS_READ()  (rs64_dpc_status_read_hook())
#define RSP_DPC_CLOCK_READ()   (0u)
#define RSP_DPC_BUFBUSY_READ() (0u)
#define RSP_DPC_PIPEBUSY_READ() (0u)
#define RSP_DPC_TMEM_READ()    (0u)

#endif // __cplusplus
#endif // RSP_DPC_MACROS_H
