// s7092: exhaustive differential of the RSP VU DMEM fast paths (rs64_g1e_dmem=1) vs the ares byte loops (=0),
// plus VRCP/VRCPL/VRCPH/VRSQ/VRSQL against an INDEPENDENT reference (cxd4 do_div + its MAME-derived div_ROM).
// Built by run.sh against the LIVE headers: rsp_vu.hpp, rsp_vu_impl.hpp, and the DMEM block extracted from rsp.hpp.
#include <cstdio>
#include <cstring>
#include <cstdint>
#include <cstdlib>
#include "rsp_vu.hpp"
static uint8_t g_dm[0x2000]; // 0x1000 used; second page only catches a mutated (unmasked) helper in the control
#define RS64_DMEM_BASE g_dm
extern "C" int rs64_g1e_dmem; int rs64_g1e_dmem = 1;
#define RS64_RSP_HOOKS_GATE rs64_rsp_hooks_on
extern "C" int rs64_rsp_hooks_on; int rs64_rsp_hooks_on = 0;
extern "C" void rs64_m5_audio_dmem_store(uint32_t, uint32_t, uint32_t, uint32_t) {}
extern "C" void rs64_m5_audio_dmem_vector_store(uint32_t, uint32_t, uint32_t) {}
extern "C" void rs64_spike_sdv_note(uint32_t, uint32_t, const uint32_t*) {}
extern "C" int rs64_sdv_snap_enabled(void) { return 0; }
extern "C" int rs64_vu_ring_enabled(void) { return 0; }
extern "C" void rs64_vld_note(uint32_t, uint32_t, const char*) {}
extern "C" void rs64_vu_ring_vte(uint32_t, const uint16_t*) {}
extern "C" uint32_t rs64_vu_ring_prev_vd(void) { return 0; }
extern "C" void rs64_vu_ring_capture_prev(const uint16_t*) {}
extern "C" void rs64_vu_ring_push(uint32_t, uint32_t, uint32_t, const uint16_t*) {}
#include "dmem_block.inc"          // RSP_MEM_B/BU, rs64_dmem_*, RSP_MEM_{W,HU,H}_{LOAD,STORE} from rsp.hpp
uint16_t rspReciprocals[512], rspInverseSquareRoots[512];
#include "rsp_vu_impl.hpp"
#include "constants_init.inc"     // body of recomp::rsp::constants_init from rsp.cpp
// ---- cxd4 reference (rs64-oracle/src/mupen64plus-rsp-cxd4/vu/divide.c, extracted verbatim by run.sh) ----
typedef int32_t i32; typedef int32_t s32; typedef int64_t s64; typedef uint16_t u16;
#define NOINLINE
static s32 DivIn = 0, DivOut = 0;
enum { SP_DIV_SQRT_NO, SP_DIV_SQRT_YES };
enum { SP_DIV_PRECISION_SINGLE = 0, SP_DIV_PRECISION_DOUBLE = ~0 };
#include "cxd4_div.inc"

static uint64_t rs = 0x9E3779B97F4A7C15ull;
static uint64_t rnd() { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs; }
static RSP R;
static long g_fail = 0, g_cmp = 0;
static void randfill() { for (int i = 0; i < 0x1000; i++) g_dm[i] = (uint8_t)rnd(); }
static void vfill(RSP::r128 &v) { for (int i = 0; i < 16; i++) v.byte(i) = (uint8_t)rnd(); }

// One op, one template e: for every address 0..0xFFF (+ a high-bit alias), run fast and slow from identical state.
template<u8 E, typename F> static void mem_op(const char *nm, F f, int reps) {
    long bad = 0;
    for (int rep = 0; rep < reps; rep++) for (uint32_t a = 0; a < 0x1000; a++) {
        uint32_t addr = a | (rep & 1 ? 0x40000000u : 0); // rs+imm may carry high bits; helpers must mask
        randfill(); RSP::r128 v0; vfill(v0);
        uint8_t dm0[0x1000]; memcpy(dm0, g_dm, 0x1000);
        memset(g_dm + 0x1000, 0, 0x1000);
        RSP::r128 vf = v0; rs64_g1e_dmem = 1; f(vf, addr); uint8_t dmf[0x1000]; memcpy(dmf, g_dm, 0x1000);
        memcpy(g_dm, dm0, 0x1000);
        RSP::r128 vs = v0; rs64_g1e_dmem = 0; f(vs, addr);
        g_cmp++;
        if (memcmp(&vf, &vs, 16) || memcmp(dmf, g_dm, 0x1000) || g_dm[0x1000 + (rnd() & 0xFFF)] || memcmp(g_dm + 0x1000, g_dm + 0x1001, 0xFFF)) {
            if (bad < 3) printf("  DIFF %s e=%d addr=%03x\n", nm, E, addr);
            bad++;
        }
    }
    g_fail += bad;
    if (bad) printf("%s e=%d bad=%ld\n", nm, E, bad);
}
#define LD(OP) mem_op<E>(#OP, [](RSP::r128 &v, uint32_t a) { R.OP<E>(v, a, 0); }, 2)
#define ST(OP) mem_op<E>(#OP, [](RSP::r128 &v, uint32_t a) { R.OP<E>(v, a, 0); }, 2)
template<u8 E> static void all_e() {
    LD(LBV); LD(LDV); LD(LLV); LD(LQV); LD(LRV); LD(LSV); LD(LUV); LD(LPV); LD(LHV); LD(LFV); LD(LWV);
    ST(SBV); ST(SDV); ST(SLV); ST(SQV); ST(SSV); ST(SUV); ST(SPV); ST(SHV); ST(SRV); ST(SFV);
}
template<u8... Es> static void sweep(std::integer_sequence<u8, Es...>) { (all_e<Es>(), ...); }

static void scalar_mem() { // RSP_MEM_{W,HU,H}_{LOAD,STORE}: fast vs byte loop, every address
    long bad = 0;
    for (int rep = 0; rep < 2; rep++) for (uint32_t a = 0; a < 0x1000; a++) {
        uint32_t addr = a | (rep ? 0x40000000u : 0), val = (uint32_t)rnd();
        randfill(); uint8_t dm0[0x1000]; memcpy(dm0, g_dm, 0x1000);
        rs64_g1e_dmem = 1; uint32_t w1 = RSP_MEM_W_LOAD(0, addr), hu1 = RSP_MEM_HU_LOAD(0, addr), h1 = RSP_MEM_H_LOAD(0, addr);
        rs64_g1e_dmem = 0; uint32_t w0 = RSP_MEM_W_LOAD(0, addr), hu0 = RSP_MEM_HU_LOAD(0, addr), h0 = RSP_MEM_H_LOAD(0, addr);
        g_cmp += 3;
        if (w1 != w0 || hu1 != hu0 || h1 != h0) { if (bad < 3) printf("  DIFF scalar load addr=%03x\n", addr); bad++; }
        rs64_g1e_dmem = 1; RSP_MEM_W_STORE(0, addr, val); uint8_t d1[0x1000]; memcpy(d1, g_dm, 0x1000);
        memcpy(g_dm, dm0, 0x1000); rs64_g1e_dmem = 0; RSP_MEM_W_STORE(0, addr, val);
        if (memcmp(d1, g_dm, 0x1000)) { if (bad < 3) printf("  DIFF W_STORE addr=%03x\n", addr); bad++; }
        memcpy(g_dm, dm0, 0x1000); rs64_g1e_dmem = 1; RSP_MEM_H_STORE(0, addr, val); memcpy(d1, g_dm, 0x1000);
        memcpy(g_dm, dm0, 0x1000); rs64_g1e_dmem = 0; RSP_MEM_H_STORE(0, addr, val);
        if (memcmp(d1, g_dm, 0x1000)) { if (bad < 3) printf("  DIFF H_STORE addr=%03x\n", addr); bad++; }
        g_cmp += 2;
    }
    g_fail += bad; printf("scalar W/HU/H load+store: bad=%ld\n", bad);
}

// Divide unit vs cxd4. Single precision: all 65536 inputs, VRCP and VRSQ. Double precision: all 2^32 (hi,lo) pairs
// through VRCPH->VRCPL (and VRSQH->VRSQL); compares the full 32-bit DivOut (low via vd lane, high via the next VRCPH).
template<u8 E> static long div_single(bool sq) {
    long bad = 0; RSP::r128 vt{}, vd{};
    for (uint32_t x = 0; x < 0x10000; x++) {
        vt.element(E & 7) = (uint16_t)x;
        if (sq) R.VRSQ<E>(vd, 3, vt); else R.VRCP<E>(vd, 3, vt);
        uint16_t lo = vd.element(3); RSP::r128 vh{}; R.VRCPH<E>(vh, 5, vt); uint16_t hi = vh.element(5);
        uint32_t ares = (uint32_t)hi << 16 | lo;
        DivIn = (i32)(int16_t)x; do_div(DivIn, sq ? SP_DIV_SQRT_YES : SP_DIV_SQRT_NO, SP_DIV_PRECISION_SINGLE);
        g_cmp++;
        if (ares != (uint32_t)DivOut) { if (bad < 3) printf("  DIFF %s in=%04x ares=%08x cxd4=%08x\n", sq ? "VRSQ" : "VRCP", x, ares, DivOut); bad++; }
    }
    return bad;
}
template<u8 E> static long div_double(bool sq, uint32_t step) {
    long bad = 0; RSP::r128 vt{}, vd{}, vh{};
    for (uint64_t x = 0; x < 0x100000000ull; x += step) {
        uint32_t in = (uint32_t)x;
        vt.element(E & 7) = (uint16_t)(in >> 16);
        if (sq) R.VRSQH<E>(vh, 1, vt); else R.VRCPH<E>(vh, 1, vt);
        vt.element(E & 7) = (uint16_t)in;
        if (sq) R.VRSQL<E>(vd, 3, vt); else R.VRCPL<E>(vd, 3, vt);
        uint16_t lo = vd.element(3); R.VRCPH<E>(vh, 5, vt); uint16_t hi = vh.element(5);
        uint32_t ares = (uint32_t)hi << 16 | lo;
        DivIn = (i32)in; do_div(DivIn, sq ? SP_DIV_SQRT_YES : SP_DIV_SQRT_NO, SP_DIV_PRECISION_DOUBLE);
        g_cmp++;
        if (ares != (uint32_t)DivOut) { if (bad < 3) printf("  DIFF %sL in=%08x ares=%08x cxd4=%08x\n", sq ? "VRSQ" : "VRCP", in, ares, DivOut); bad++; }
    }
    return bad;
}
// VRCPL with no preceding VRCPH must act single-precision (DIVDP cleared by the previous divide)
template<u8 E> static long div_l_after_single() {
    long bad = 0; RSP::r128 vt{}, vd{};
    for (uint32_t x = 0; x < 0x10000; x++) {
        vt.element(E & 7) = 7; R.VRCP<E>(vd, 0, vt);           // clears DIVDP
        vt.element(E & 7) = (uint16_t)x; R.VRCPL<E>(vd, 3, vt);
        uint16_t lo = vd.element(3); RSP::r128 vh{}; R.VRCPH<E>(vh, 5, vt); uint32_t ares = (uint32_t)vh.element(5) << 16 | lo;
        DivIn = (i32)(int16_t)x; do_div(DivIn, SP_DIV_SQRT_NO, SP_DIV_PRECISION_SINGLE);
        g_cmp++; if (ares != (uint32_t)DivOut) bad++;
    }
    return bad;
}

int main(int argc, char **argv) {
    uint32_t step = argc > 1 ? (uint32_t)strtoul(argv[1], 0, 0) : 1;
    recomp_constants_init();
    sweep(std::make_integer_sequence<u8, 16>{});
    printf("vector load/store x16 e x8192 addr: cumulative bad=%ld\n", g_fail);
    scalar_mem();
    long d = 0;
    d += div_single<8>(false); d += div_single<11>(false); d += div_single<8>(true);
    d += div_l_after_single<12>();
    d += div_double<8>(false, step); d += div_double<15>(true, step);
    printf("divide vs cxd4: bad=%ld (double-precision step %u)\n", d, step);
    g_fail += d;
    printf("TOTAL compares=%ld bad=%ld\n", g_cmp, g_fail);
    return g_fail ? 1 : 0;
}
