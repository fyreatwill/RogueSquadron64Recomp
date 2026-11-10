// s6301: differential fuzz of the RSP VU SIMD vs SISD paths (ares-derived rsp_vu_impl.hpp).
// Built twice with rsp_vu.hpp's Accuracy flags flipped; prints one state-hash per op/element.
#include <cstdio>
#include <cstring>
#include <cstdint>
#include <cstdlib>
#include "rsp_vu.hpp"
static uint8_t g_dmem[0x2000];
#define RSP_MEM_BU(a, b) g_dmem[(b) & 0xFFF]
#define RSP_MEM_B(a, b) ((int8_t&)g_dmem[(b) & 0xFFF])
#define RSP_MEM_HU(a, b) (*(uint16_t*)&g_dmem[(b) & 0xFFE])
#define RSP_MEM_H(a, b) (*(int16_t*)&g_dmem[(b) & 0xFFE])
#define RSP_MEM_W(a, b) (*(int32_t*)&g_dmem[(b) & 0xFFC])
#define RSP_MEM_WU(a, b) (*(uint32_t*)&g_dmem[(b) & 0xFFC])
static void rs64_m5_audio_dmem_vector_store(...) {}
// s7092: symbols the live rsp_vu_impl.hpp now references (loads/stores are not exercised here; tools/s7092_vu_mem_test covers them)
extern "C" int rs64_rsp_hooks_on; int rs64_rsp_hooks_on = 0; static int rs64_g1e_dmem = 0;
static uint32_t rs64_dmem_w(uint32_t) { return 0; } static void rs64_dmem_w_set(uint32_t, uint32_t) {}
static uint16_t rs64_dmem_h(uint32_t) { return 0; } static void rs64_dmem_h_set(uint32_t, uint16_t) {}
extern "C" void rs64_spike_sdv_note(uint32_t, uint32_t, const uint32_t*) {}
extern "C" int rs64_sdv_snap_enabled(void) { return 0; }
extern "C" int rs64_vu_ring_enabled(void) { return 0; }
extern "C" void rs64_vld_note(uint32_t, uint32_t, const char*) {}
extern "C" void rs64_vu_ring_vte(uint32_t, const uint16_t*) {}
extern "C" uint32_t rs64_vu_ring_prev_vd(void) { return 0; }
extern "C" void rs64_vu_ring_capture_prev(const uint16_t*) {}
extern "C" void rs64_vu_ring_push(uint32_t, uint32_t, uint32_t, const uint16_t*) {}
static uint16_t rspReciprocals[512]; static uint16_t rspInverseSquareRoots[512];
#include "rsp_vu_impl.hpp"
static uint64_t rs = 0x9E3779B97F4A7C15ull;
static uint64_t rnd() { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs; }
static uint16_t lane() {
    static const uint16_t sp[] = {0, 1, 0xFFFF, 0x7FFF, 0x8000, 0x8001, 0x7FFE, 2, 0xFFFE};
    uint64_t r = rnd(); return (r & 3) == 0 ? sp[(r >> 8) % 9] : (uint16_t)(r >> 16);
}
static void fill(RSP::r128 &v) { for (int i = 0; i < 8; i++) v.u16(i) = lane(); }
static void flag(RSP::r128 &v) { for (int i = 0; i < 8; i++) v.u16(i) = (rnd() >> 20) & 1 ? 0xFFFF : 0; }
static uint64_t H;
static void mix(const RSP::r128 &v) { for (int i = 0; i < 2; i++) { H ^= v.u128[i]; H *= 0x100000001B3ull; H ^= H >> 29; } }
static RSP R;
static void snap(const RSP::r128 &vd) {
    mix(vd); mix(R.vpu.acch); mix(R.vpu.accm); mix(R.vpu.accl); mix(R.vpu.vcoh); mix(R.vpu.vcol); mix(R.vpu.vcch); mix(R.vpu.vccl); mix(R.vpu.vce);
}
template<u8 E> static void run_e(const char *name, void (RSP::*f)(RSP::r128 &, const RSP::r128 &, const RSP::r128 &)) {
    rs = 0x1234567 + E * 7919; H = 14695981039346656037ull;
    for (int it = 0; it < 200000; it++) {
        RSP::r128 vs, vt, vd{}; fill(vs); fill(vt);
        fill(R.vpu.acch); fill(R.vpu.accm); fill(R.vpu.accl);
        flag(R.vpu.vcoh); flag(R.vpu.vcol); flag(R.vpu.vcch); flag(R.vpu.vccl); flag(R.vpu.vce);
        (R.*f)(vd, vs, vt); snap(vd);
    }
    printf("%s e=%d %016llx\n", name, E, (unsigned long long)H);
}
#define OP(N) run_e<E>(#N, &RSP::N<E>)
template<u8 E> static void all() {
    OP(VABS); OP(VADD); OP(VADDC); OP(VAND); OP(VCH); OP(VCL); OP(VCR); OP(VEQ); OP(VGE); OP(VLT);
    OP(VMACF); OP(VMACU); OP(VMADH); OP(VMADL); OP(VMADM); OP(VMADN); OP(VMRG); OP(VMUDH); OP(VMUDL); OP(VMUDM); OP(VMUDN);
    OP(VMULF); OP(VMULU); OP(VNAND); OP(VNE); OP(VNOR); OP(VNXOR); OP(VOR); OP(VSUB); OP(VSUBC); OP(VXOR);
}
template<u8... Es> static void sweep(std::integer_sequence<u8, Es...>) { (all<Es>(), ...); }
int main() { sweep(std::make_integer_sequence<u8, 16>{}); }
